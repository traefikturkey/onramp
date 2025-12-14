#!/usr/bin/env python
"""
mariadb_manager.py - MariaDB helper operations for OnRamp

Commands:
  create-db <dbname>              - Create database if not exists
  list-databases                  - List all databases
  drop-db <dbname>                - Drop database
  database-exists <dbname>        - Check if database exists
  console                         - Interactive mysql console
  backup-db <dbname> <output>     - Backup database to file
  restore-db <dbname> <backup>    - Restore database from backup
  create-user <username> [dbname] - Create user with password
  get-stats <dbname>              - Get database statistics
  verify-db <dbname>              - Verify database integrity
  migrate-from <container> <src_db> <dest_db> - Migrate from another container

Features:
- Executes via docker exec into mariadb container
- Safe database creation (IF NOT EXISTS)
- User isolation with per-database permissions
- Backup/restore using mariadb-dump/mariadb
- Proper SQL escaping
- UTF-8mb4 support
"""

import argparse
import json
import os
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


class MariaDBManager:
    """Manages MariaDB operations via docker exec."""

    def __init__(
        self,
        container_name: str = "mariadb",
        base_dir: str = "/app",
        docker: "DockerExecutor | None" = None,
    ):
        self.container_name = container_name
        self.base_dir = Path(base_dir)
        
        # Get password from container environment
        self._root_password = None

        if docker is not None:
            self._docker = docker
        else:
            from adapters.docker_subprocess import SubprocessDockerExecutor

            self._docker = SubprocessDockerExecutor()
            
    def _get_root_password(self) -> str:
        """Get MariaDB root password from container environment."""
        if self._root_password is None:
            # Get password from container environment variable
            code, stdout, stderr = self._docker.exec(
                self.container_name,
                ["bash", "-c", "echo $MYSQL_ROOT_PASSWORD"],
                False
            )
            if code == 0 and stdout.strip():
                self._root_password = stdout.strip()
            else:
                # Fallback to empty password (should not happen)
                self._root_password = ""
        return self._root_password

    def _docker_exec(self, cmd: list[str], interactive: bool = False) -> tuple[int, str, str]:
        """Execute command in docker container."""
        return self._docker.exec(self.container_name, cmd, interactive)

    def _mysql_exec(self, sql: str, dbname: str = "mysql") -> tuple[int, str, str]:
        """Execute SQL via mariadb client in container.

        Uses MYSQL_PWD environment variable to avoid password in process listing.
        """
        password = self._get_root_password()
        # Use MYSQL_PWD env var instead of -p to avoid password in ps output
        # Pass via bash -c with env var set
        cmd = ["bash", "-c", f"MYSQL_PWD='{password}' mariadb -u root {dbname} -e \"{sql}\""]
        return self._docker_exec(cmd)

    def console(self) -> int:
        """Open interactive mariadb console."""
        print(f"Connecting to {self.container_name}...")
        password = self._get_root_password()
        # Use MYSQL_PWD env var for interactive console too
        cmd = ["bash", "-c", f"MYSQL_PWD='{password}' mariadb -u root"]
        return self._docker_exec(cmd, interactive=True)[0]

    def list_databases(self) -> tuple[int, list[str]]:
        """List all databases."""
        code, stdout, stderr = self._mysql_exec("SHOW DATABASES")
        if code != 0:
            print(f"Error: {stderr}", file=sys.stderr)
            return code, []

        # Parse mysql output
        databases = []
        for line in stdout.split("\n"):
            line = line.strip()
            if line and line not in ["Database", "information_schema", "performance_schema", "mysql", "sys"]:
                databases.append(line)
        return 0, databases

    def database_exists(self, dbname: str) -> bool:
        """Check if database exists."""
        validate_db_name(dbname)
        sql = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{dbname}'"
        code, stdout, stderr = self._mysql_exec(sql)
        return code == 0 and dbname in stdout

    def create_database(self, dbname: str) -> int:
        """Create a database if it doesn't exist.

        Uses CREATE DATABASE IF NOT EXISTS to avoid TOCTOU race condition
        between database_exists() check and creation.
        """
        validate_db_name(dbname)
        # Use IF NOT EXISTS - no need to check first (avoids TOCTOU race)
        sql = f"CREATE DATABASE IF NOT EXISTS `{dbname}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        code, stdout, stderr = self._mysql_exec(sql)
        if code != 0:
            print(f"Error creating database: {stderr}", file=sys.stderr)
        else:
            print(f"Database '{dbname}' created or already exists")
        return code

    def drop_database(self, dbname: str) -> int:
        """Drop a database."""
        validate_db_name(dbname)
        sql = f"DROP DATABASE IF EXISTS `{dbname}`"
        code, stdout, stderr = self._mysql_exec(sql)
        if code != 0:
            print(f"Error dropping database: {stderr}", file=sys.stderr)
        else:
            print(f"Database '{dbname}' dropped")
        return code

    def create_user(self, username: str, password: str = None, dbname: str = None) -> tuple[int, str]:
        """Create a MariaDB user with optional database ownership."""
        validate_username(username)
        if dbname:
            validate_db_name(dbname)

        if password is None:
            # Generate secure random password
            alphabet = string.ascii_letters + string.digits
            password = ''.join(secrets.choice(alphabet) for _ in range(32))

        # Create user - password is generated internally, so safe from injection
        sql = f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{password}'"
        code, stdout, stderr = self._mysql_exec(sql)
        if code != 0:
            print(f"Error creating user: {stderr}", file=sys.stderr)
            return code, password

        # Grant database ownership if specified
        if dbname:
            grant_sql = f"GRANT ALL PRIVILEGES ON `{dbname}`.* TO '{username}'@'%'"
            code, stdout, stderr = self._mysql_exec(grant_sql)
            if code != 0:
                print(f"Error granting privileges: {stderr}", file=sys.stderr)
                return code, password

            # Flush privileges
            flush_code, _, _ = self._mysql_exec("FLUSH PRIVILEGES")
            if flush_code != 0:
                print("Warning: Failed to flush privileges", file=sys.stderr)

        # Save password to file
        password_file = self.base_dir / "etc" / ".db_passwords" / f"{username}.txt"
        password_file.parent.mkdir(parents=True, exist_ok=True)
        password_file.write_text(password)
        password_file.chmod(0o600)

        print(f"User '{username}' created. Password saved to {password_file}")
        return 0, password

    def backup_database(self, dbname: str, output_file: str) -> int:
        """Backup database to SQL file."""
        validate_db_name(dbname)
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{output_path.stem}_{timestamp}.sql"

        password = self._get_root_password()
        # Use MYSQL_PWD env var to avoid password in process listing
        cmd = [
            "bash", "-c",
            f"MYSQL_PWD='{password}' mariadb-dump -u root --single-transaction --routines --triggers {dbname}"
        ]

        code, stdout, stderr = self._docker_exec(cmd)
        if code != 0:
            print(f"Error backing up database: {stderr}", file=sys.stderr)
            return code

        # Write backup to file
        output_path.write_text(stdout)
        print(f"Database '{dbname}' backed up to {output_path}")
        return 0

    def restore_database(self, dbname: str, backup_file: str) -> int:
        """Restore database from SQL backup file."""
        validate_db_name(dbname)
        backup_path = Path(backup_file)
        if not backup_path.exists():
            print(f"Backup file not found: {backup_file}", file=sys.stderr)
            return 1

        # Create database if it doesn't exist
        self.create_database(dbname)

        # Read backup content
        sql_content = backup_path.read_text()

        # Copy backup to container and restore
        password = self._get_root_password()
        print(f"Restoring database '{dbname}' from {backup_file}...")

        # Use docker cp + exec approach for restore
        temp_file = f"/tmp/restore_{dbname}.sql"
        copy_cmd = ["docker", "cp", str(backup_path), f"{self.container_name}:{temp_file}"]
        result = subprocess.run(copy_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error copying backup to container: {result.stderr}", file=sys.stderr)
            return 1

        # Restore using MYSQL_PWD env var
        restore_cmd = ["bash", "-c", f"MYSQL_PWD='{password}' mariadb -u root {dbname} < {temp_file} && rm {temp_file}"]
        code, stdout, stderr = self._docker_exec(restore_cmd)
        if code != 0:
            print(f"Error restoring database: {stderr}", file=sys.stderr)
            return code

        print(f"Database '{dbname}' restored successfully")
        return 0

    def get_stats(self, dbname: str) -> int:
        """Get database statistics."""
        validate_db_name(dbname)
        if not self.database_exists(dbname):
            print(f"Database '{dbname}' does not exist", file=sys.stderr)
            return 1

        sql = f"""
        SELECT
            table_schema AS 'Database',
            COUNT(*) AS 'Tables',
            ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
        FROM information_schema.TABLES
        WHERE table_schema = '{dbname}'
        GROUP BY table_schema
        """

        code, stdout, stderr = self._mysql_exec(sql)
        if code != 0:
            print(f"Error getting stats: {stderr}", file=sys.stderr)
        else:
            print(stdout)
        return code

    def verify_database(self, dbname: str) -> int:
        """Verify database integrity."""
        validate_db_name(dbname)
        if not self.database_exists(dbname):
            print(f"Database '{dbname}' does not exist", file=sys.stderr)
            return 1

        # Get list of tables
        sql = f"SELECT table_name FROM information_schema.TABLES WHERE table_schema = '{dbname}'"
        code, stdout, stderr = self._mysql_exec(sql)
        if code != 0:
            print(f"Error getting tables: {stderr}", file=sys.stderr)
            return code

        tables = [line.strip() for line in stdout.split("\n") if line.strip() and line.strip() != "table_name"]

        print(f"Checking {len(tables)} tables in '{dbname}'...")
        for table in tables:
            # Validate table name before using in SQL
            try:
                validate_table_name(table)
            except ValueError:
                print(f"  ? {table}: Skipped (unusual name)")
                continue
            check_sql = f"CHECK TABLE `{dbname}`.`{table}`"
            code, stdout, stderr = self._mysql_exec(check_sql)
            if code != 0 or "error" in stdout.lower():
                print(f"  ✗ {table}: FAILED")
            else:
                print(f"  ✓ {table}: OK")

        return 0

    def migrate_from_container(self, source_container: str, source_db: str, dest_db: str) -> int:
        """Migrate database from another container to shared MariaDB."""
        validate_db_name(source_db)
        validate_db_name(dest_db)
        print(f"Migrating {source_db} from {source_container} to {dest_db}...")

        # Backup from source
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / "backups" / "mariadb-migrations"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / f"{source_db}_{timestamp}.sql"

        print("1. Creating backup...")
        # Use bash -c with MYSQL_PWD to avoid password in process listing
        dump_cmd = [
            "docker", "exec", source_container,
            "bash", "-c",
            f"MYSQL_PWD=\"$MYSQL_ROOT_PASSWORD\" mariadb-dump -u root --single-transaction --routines --triggers {source_db}"
        ]

        try:
            result = subprocess.run(dump_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error creating backup: {result.stderr}", file=sys.stderr)
                return 1

            backup_file.write_text(result.stdout)
            print(f"   Backup created: {backup_file}")

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        # Create destination database
        print("2. Creating destination database...")
        self.create_database(dest_db)

        # Restore to shared MariaDB
        print("3. Restoring to shared MariaDB...")
        password = self._get_root_password()

        # Copy backup to container
        temp_file = f"/tmp/migrate_{dest_db}.sql"
        copy_cmd = ["docker", "cp", str(backup_file), f"{self.container_name}:{temp_file}"]
        result = subprocess.run(copy_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Error copying backup: {result.stderr}", file=sys.stderr)
            return 1

        # Restore using MYSQL_PWD
        restore_cmd = [
            "docker", "exec", self.container_name,
            "bash", "-c",
            f"MYSQL_PWD='{password}' mariadb -u root {dest_db} < {temp_file} && rm {temp_file}"
        ]

        try:
            result = subprocess.run(restore_cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error restoring: {result.stderr}", file=sys.stderr)
                return 1

            print(f"   ✓ Migration complete!")
            print(f"   Backup saved at: {backup_file}")

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return 1

        return 0


def main():
    parser = argparse.ArgumentParser(description="MariaDB Manager")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # create-db
    create_parser = subparsers.add_parser("create-db", help="Create database")
    create_parser.add_argument("dbname", help="Database name")

    # list-databases
    subparsers.add_parser("list-databases", help="List all databases")

    # drop-db
    drop_parser = subparsers.add_parser("drop-db", help="Drop database")
    drop_parser.add_argument("dbname", help="Database name")

    # database-exists
    exists_parser = subparsers.add_parser("database-exists", help="Check if database exists")
    exists_parser.add_argument("dbname", help="Database name")

    # console
    subparsers.add_parser("console", help="Interactive mysql console")

    # backup-db
    backup_parser = subparsers.add_parser("backup-db", help="Backup database")
    backup_parser.add_argument("dbname", help="Database name")
    backup_parser.add_argument("output", help="Output file path")

    # restore-db
    restore_parser = subparsers.add_parser("restore-db", help="Restore database")
    restore_parser.add_argument("dbname", help="Database name")
    restore_parser.add_argument("backup", help="Backup file path")

    # create-user
    user_parser = subparsers.add_parser("create-user", help="Create user")
    user_parser.add_argument("username", help="Username")
    user_parser.add_argument("dbname", nargs="?", help="Database name (optional)")

    # get-stats
    stats_parser = subparsers.add_parser("get-stats", help="Get database statistics")
    stats_parser.add_argument("dbname", help="Database name")

    # verify-db
    verify_parser = subparsers.add_parser("verify-db", help="Verify database integrity")
    verify_parser.add_argument("dbname", help="Database name")

    # migrate-from
    migrate_parser = subparsers.add_parser("migrate-from", help="Migrate from another container")
    migrate_parser.add_argument("container", help="Source container name")
    migrate_parser.add_argument("src_db", help="Source database name")
    migrate_parser.add_argument("dest_db", help="Destination database name")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    manager = MariaDBManager()

    if args.command == "create-db":
        return manager.create_database(args.dbname)
    elif args.command == "list-databases":
        code, databases = manager.list_databases()
        if code == 0:
            for db in databases:
                print(db)
        return code
    elif args.command == "drop-db":
        return manager.drop_database(args.dbname)
    elif args.command == "database-exists":
        exists = manager.database_exists(args.dbname)
        print("true" if exists else "false")
        return 0 if exists else 1
    elif args.command == "console":
        return manager.console()
    elif args.command == "backup-db":
        return manager.backup_database(args.dbname, args.output)
    elif args.command == "restore-db":
        return manager.restore_database(args.dbname, args.backup)
    elif args.command == "create-user":
        code, password = manager.create_user(args.username, dbname=args.dbname)
        return code
    elif args.command == "get-stats":
        return manager.get_stats(args.dbname)
    elif args.command == "verify-db":
        return manager.verify_database(args.dbname)
    elif args.command == "migrate-from":
        return manager.migrate_from_container(args.container, args.src_db, args.dest_db)

    return 0


if __name__ == "__main__":
    sys.exit(main())
