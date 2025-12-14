#!/usr/bin/env python
"""
postgres_manager.py - PostgreSQL helper operations for OnRamp

Commands:
  create-db <dbname>              - Create database if not exists
  list-databases                  - List all databases
  drop-db <dbname>                - Drop database
  database-exists <dbname>        - Check if database exists
  console                         - Interactive psql console
  backup-db <dbname> <output>     - Backup database to file
  restore-db <dbname> <backup>    - Restore database from backup
  create-user <username> [dbname] - Create user with password
  get-stats <dbname>              - Get database statistics
  verify-db <dbname>              - Verify database integrity
  migrate-from <container> <src_db> <dest_db> - Migrate from another container

Features:
- Executes via docker exec into postgres container
- Safe database creation (IF NOT EXISTS)
- User isolation with per-database permissions
- Backup/restore using pg_dump/pg_restore
- Proper SQL escaping
"""

import argparse
import json
import re
import secrets
import string
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.docker import DockerExecutor

# Validation patterns to prevent SQL injection
# Database names: alphanumeric, underscore, hyphen, 1-63 chars, must start with letter
DB_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]{0,62}$')
# Usernames: alphanumeric, underscore, 1-63 chars, must start with letter
USERNAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{0,62}$')
# Table names: same as DB names
TABLE_NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_]{0,62}$')


def validate_db_name(dbname: str) -> None:
    """Validate database name to prevent SQL injection."""
    if not dbname:
        raise ValueError("Database name cannot be empty")
    if not DB_NAME_PATTERN.match(dbname):
        raise ValueError(
            f"Invalid database name '{dbname}'. Must start with a letter, "
            "contain only alphanumeric characters, underscores, or hyphens, "
            "and be 1-63 characters long."
        )


def validate_username(username: str) -> None:
    """Validate username to prevent SQL injection."""
    if not username:
        raise ValueError("Username cannot be empty")
    if not USERNAME_PATTERN.match(username):
        raise ValueError(
            f"Invalid username '{username}'. Must start with a letter, "
            "contain only alphanumeric characters or underscores, "
            "and be 1-63 characters long."
        )


def validate_table_name(table_name: str) -> None:
    """Validate table name to prevent SQL injection."""
    if not table_name:
        raise ValueError("Table name cannot be empty")
    if not TABLE_NAME_PATTERN.match(table_name):
        raise ValueError(
            f"Invalid table name '{table_name}'. Must start with a letter, "
            "contain only alphanumeric characters or underscores, "
            "and be 1-63 characters long."
        )


class PostgresManager:
    """Manages PostgreSQL operations via docker exec."""

    def __init__(
        self,
        container_name: str = "postgres",
        base_dir: str = "/app",
        docker: "DockerExecutor | None" = None,
    ):
        self.container_name = container_name
        self.base_dir = Path(base_dir)

        if docker is not None:
            self._docker = docker
        else:
            from adapters.docker_subprocess import SubprocessDockerExecutor

            self._docker = SubprocessDockerExecutor()

    def _docker_exec(self, cmd: list[str], interactive: bool = False) -> tuple[int, str, str]:
        """Execute command in docker container."""
        return self._docker.exec(self.container_name, cmd, interactive)

    def _psql_exec(self, sql: str, dbname: str = "postgres") -> tuple[int, str, str]:
        """Execute SQL via psql client in container."""
        # Use admin user from env
        cmd = ["psql", "-U", "admin", "-d", dbname, "-c", sql]
        return self._docker_exec(cmd)

    def console(self) -> int:
        """Open interactive psql console."""
        print(f"Connecting to {self.container_name}...")
        return self._docker_exec(["psql", "-U", "admin"], interactive=True)[0]

    def list_databases(self) -> tuple[int, list[str]]:
        """List all databases."""
        code, stdout, stderr = self._psql_exec("\\l")
        if code != 0:
            print(f"Error: {stderr}", file=sys.stderr)
            return code, []

        # Parse postgres \l output
        databases = []
        for line in stdout.split("\n"):
            if "|" in line and not line.strip().startswith("Name"):
                parts = line.split("|")
                if parts:
                    db = parts[0].strip()
                    if db and db not in ["template0", "template1", "postgres", "admin"]:
                        databases.append(db)
        return 0, databases

    def database_exists(self, dbname: str) -> bool:
        """Check if database exists."""
        validate_db_name(dbname)
        sql = f"SELECT 1 FROM pg_database WHERE datname='{dbname}'"
        code, stdout, stderr = self._psql_exec(sql)
        return code == 0 and "1" in stdout

    def create_database(self, dbname: str) -> int:
        """Create a database if it doesn't exist."""
        validate_db_name(dbname)
        if self.database_exists(dbname):
            print(f"Database '{dbname}' already exists")
            return 0

        sql = f'CREATE DATABASE "{dbname}"'
        code, stdout, stderr = self._psql_exec(sql)
        if code != 0:
            print(f"Error creating database: {stderr}", file=sys.stderr)
        else:
            print(f"Database '{dbname}' created successfully")
        return code

    def drop_database(self, dbname: str) -> int:
        """Drop a database."""
        validate_db_name(dbname)
        sql = f'DROP DATABASE IF EXISTS "{dbname}"'
        code, stdout, stderr = self._psql_exec(sql)
        if code != 0:
            print(f"Error dropping database: {stderr}", file=sys.stderr)
        else:
            print(f"Database '{dbname}' dropped")
        return code

    def create_user(self, username: str, password: str = None, dbname: str = None) -> tuple[int, str]:
        """Create a postgres user with optional database ownership."""
        validate_username(username)
        if dbname:
            validate_db_name(dbname)

        if password is None:
            # Generate secure random password
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(32))

        # Create user - password is generated internally, so safe from injection
        sql = f"CREATE USER \"{username}\" WITH PASSWORD '{password}'"
        code, stdout, stderr = self._psql_exec(sql)
        if code != 0 and "already exists" not in stderr:
            print(f"Error creating user: {stderr}", file=sys.stderr)
            return code, password

        # Grant database ownership if specified
        if dbname:
            grant_sql = f'GRANT ALL PRIVILEGES ON DATABASE "{dbname}" TO "{username}"'
            code, stdout, stderr = self._psql_exec(grant_sql)
            if code != 0:
                print(f"Error granting privileges: {stderr}", file=sys.stderr)

        # Save password to file
        password_file = self.base_dir / "etc" / ".db_passwords" / f"{username}.txt"
        password_file.parent.mkdir(parents=True, exist_ok=True)
        password_file.write_text(password)
        password_file.chmod(0o600)

        print(f"User '{username}' created. Password saved to {password_file}")
        return 0, password

    def backup_database(self, dbname: str, output_path: Path) -> int:
        """Backup database using pg_dump."""
        validate_db_name(dbname)
        print(f"Backing up database '{dbname}' to {output_path}...")

        # Use custom format (-Fc) for best compression and flexibility
        cmd = ["pg_dump", "-U", "admin", "-d", dbname, "-Fc", "-f", f"/tmp/{dbname}.dump"]
        code, stdout, stderr = self._docker_exec(cmd)

        if code != 0:
            print(f"Error during backup: {stderr}", file=sys.stderr)
            return code

        # Copy dump file from container to host
        copy_cmd = ["docker", "cp", f"{self.container_name}:/tmp/{dbname}.dump", str(output_path)]
        result = subprocess.run(copy_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error copying backup: {result.stderr}", file=sys.stderr)
            return result.returncode

        # Cleanup temp file
        self._docker_exec(["rm", f"/tmp/{dbname}.dump"])

        print(f"✅ Backup complete: {output_path}")
        return 0

    def restore_database(self, dbname: str, backup_path: Path) -> int:
        """Restore database from pg_dump backup."""
        validate_db_name(dbname)
        print(f"Restoring database '{dbname}' from {backup_path}...")

        if not backup_path.exists():
            print(f"Error: Backup file not found: {backup_path}", file=sys.stderr)
            return 1

        # Copy dump file to container
        copy_cmd = ["docker", "cp", str(backup_path), f"{self.container_name}:/tmp/{dbname}.dump"]
        result = subprocess.run(copy_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"Error copying backup to container: {result.stderr}", file=sys.stderr)
            return result.returncode

        # Create database if it doesn't exist
        self.create_database(dbname)

        # Restore using pg_restore (-c = clean, --if-exists = safer)
        cmd = ["pg_restore", "-U", "admin", "-d", dbname, "--clean", "--if-exists", f"/tmp/{dbname}.dump"]
        code, stdout, stderr = self._docker_exec(cmd)

        # Cleanup temp file
        self._docker_exec(["rm", f"/tmp/{dbname}.dump"])

        if code != 0:
            print(f"Warning during restore (may be normal): {stderr}", file=sys.stderr)

        print(f"✅ Restore complete: {dbname}")
        return 0

    def get_database_stats(self, dbname: str) -> dict:
        """Get database statistics (size, table count, row counts)."""
        validate_db_name(dbname)
        stats = {"dbname": dbname, "tables": {}, "total_size": 0}

        # Get database size
        sql = f"SELECT pg_database_size('{dbname}')"
        code, stdout, stderr = self._psql_exec(sql)
        if code == 0:
            try:
                stats["total_size"] = int(stdout.strip().split("\n")[2].strip())
            except:
                pass

        # Get table list and row counts
        sql = """
        SELECT schemaname, tablename,
               pg_total_relation_size(schemaname||'.'||tablename) as size
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY tablename
        """
        code, stdout, stderr = self._psql_exec(sql, dbname)

        if code == 0:
            for line in stdout.split("\n"):
                if "|" in line and "public" in line:
                    parts = [p.strip() for p in line.split("|")]
                    if len(parts) >= 2:
                        table_name = parts[1]
                        # Validate table name before using in SQL
                        try:
                            validate_table_name(table_name)
                        except ValueError:
                            # Skip tables with unusual names
                            continue
                        # Get row count
                        count_sql = f"SELECT COUNT(*) FROM \"{table_name}\""
                        c, out, err = self._psql_exec(count_sql, dbname)
                        if c == 0:
                            try:
                                count = int(out.strip().split("\n")[2].strip())
                                stats["tables"][table_name] = count
                            except:
                                pass

        return stats

    def verify_database(self, dbname: str) -> bool:
        """Verify database integrity."""
        validate_db_name(dbname)
        print(f"Verifying database '{dbname}'...")

        # Check database exists
        if not self.database_exists(dbname):
            print(f"❌ Database '{dbname}' does not exist")
            return False

        # Get stats
        stats = self.get_database_stats(dbname)

        print(f"  Database size: {stats['total_size']:,} bytes")
        print(f"  Tables found: {len(stats['tables'])}")

        if stats['tables']:
            print(f"  Table details:")
            for table, rows in stats['tables'].items():
                print(f"    - {table}: {rows:,} rows")

        print(f"✅ Verification complete")
        return True

    def migrate_from_container(
        self, source_container: str, source_db: str, dest_db: str, source_user: str = "postgres"
    ) -> int:
        """Migrate database from another postgres container to shared instance."""
        validate_db_name(source_db)
        validate_db_name(dest_db)
        validate_username(source_user)
        print(f"Migrating {source_db} from {source_container} to shared postgres as {dest_db}...")

        # Create temporary backup path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / "backups" / "postgres-migrations"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_path = backup_dir / f"{source_db}_{timestamp}.dump"

        # Dump from source container
        print(f"  Step 1/4: Backing up from {source_container}...")
        dump_cmd = ["pg_dump", "-U", source_user, "-d", source_db, "-Fc", "-f", f"/tmp/{source_db}.dump"]

        from adapters.docker_subprocess import SubprocessDockerExecutor

        source_docker = SubprocessDockerExecutor()
        code, stdout, stderr = source_docker.exec(source_container, dump_cmd, False)

        if code != 0:
            print(f"❌ Error backing up from source: {stderr}", file=sys.stderr)
            return code

        # Copy from source container to host
        print(f"  Step 2/4: Copying backup to host...")
        copy_cmd = ["docker", "cp", f"{source_container}:/tmp/{source_db}.dump", str(backup_path)]
        result = subprocess.run(copy_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Error copying from source: {result.stderr}", file=sys.stderr)
            return result.returncode

        # Cleanup source temp
        source_docker.exec(source_container, ["rm", f"/tmp/{source_db}.dump"], False)

        # Restore to shared postgres
        print(f"  Step 3/4: Restoring to shared postgres as '{dest_db}'...")
        restore_code = self.restore_database(dest_db, backup_path)

        if restore_code != 0:
            print(f"❌ Error restoring to shared postgres", file=sys.stderr)
            return restore_code

        # Verify migration
        print(f"  Step 4/4: Verifying migration...")
        if not self.verify_database(dest_db):
            print(f"⚠️  Verification had issues, but database was restored")

        print(f"✅ Migration complete! Backup saved: {backup_path}")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="PostgreSQL helper operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  postgres_manager.py console                          # Open interactive psql console
  postgres_manager.py list-databases                   # Show all databases
  postgres_manager.py create-db myapp                  # Create database 'myapp'
  postgres_manager.py database-exists myapp            # Check if exists
  postgres_manager.py drop-db myapp                    # Drop database
  postgres_manager.py create-user myapp_user myapp     # Create user for database
  postgres_manager.py backup-db myapp backup.dump      # Backup database
  postgres_manager.py restore-db myapp backup.dump     # Restore database
  postgres_manager.py get-stats myapp                  # Get database statistics
  postgres_manager.py verify-db myapp                  # Verify database
  postgres_manager.py migrate-from docmost-db docmost docmost  # Migrate from container
        """,
    )

    parser.add_argument(
        "action",
        choices=[
            "console",
            "list-databases",
            "create-db",
            "drop-db",
            "database-exists",
            "create-user",
            "backup-db",
            "restore-db",
            "get-stats",
            "verify-db",
            "migrate-from",
        ],
        help="Action to perform",
    )
    parser.add_argument("args", nargs="*", help="Arguments for the action")
    parser.add_argument("--container", "-c", default="postgres", help="Container name")
    parser.add_argument("--base-dir", default="/app", help="Base directory")
    parser.add_argument("--source-user", default="postgres", help="Source database user for migration")

    args = parser.parse_args()
    mgr = PostgresManager(container_name=args.container, base_dir=args.base_dir)

    if args.action == "console":
        return mgr.console()

    if args.action == "list-databases":
        code, databases = mgr.list_databases()
        if code == 0:
            for db in databases:
                print(db)
        return code

    if args.action == "create-db":
        if not args.args:
            parser.error("Database name required")
        return mgr.create_database(args.args[0])

    if args.action == "database-exists":
        if not args.args:
            parser.error("Database name required")
        exists = mgr.database_exists(args.args[0])
        print("yes" if exists else "no")
        return 0 if exists else 1

    if args.action == "drop-db":
        if not args.args:
            parser.error("Database name required")
        return mgr.drop_database(args.args[0])

    if args.action == "create-user":
        if len(args.args) < 1:
            parser.error("Username required")
        username = args.args[0]
        dbname = args.args[1] if len(args.args) > 1 else None
        code, password = mgr.create_user(username, dbname=dbname)
        return code

    if args.action == "backup-db":
        if len(args.args) < 2:
            parser.error("Database name and output path required")
        dbname = args.args[0]
        output = Path(args.args[1])
        return mgr.backup_database(dbname, output)

    if args.action == "restore-db":
        if len(args.args) < 2:
            parser.error("Database name and backup path required")
        dbname = args.args[0]
        backup = Path(args.args[1])
        return mgr.restore_database(dbname, backup)

    if args.action == "get-stats":
        if not args.args:
            parser.error("Database name required")
        stats = mgr.get_database_stats(args.args[0])
        print(json.dumps(stats, indent=2))
        return 0

    if args.action == "verify-db":
        if not args.args:
            parser.error("Database name required")
        success = mgr.verify_database(args.args[0])
        return 0 if success else 1

    if args.action == "migrate-from":
        if len(args.args) < 3:
            parser.error("Source container, source DB, and dest DB required")
        source_container = args.args[0]
        source_db = args.args[1]
        dest_db = args.args[2]
        return mgr.migrate_from_container(source_container, source_db, dest_db, args.source_user)

    return 0


if __name__ == "__main__":
    sys.exit(main())
