#!/usr/bin/env python
"""
database.py - Database helper operations for OnRamp

Commands:
  create-user <username> [--password <pw> | --generate]
  create-db <dbname>
  grant <db> <user>
  list-users
  list-databases
  console
  remove-user <username>
  drop-db <dbname>
  setup <name>  # create user with generated password, db, and grant

Features:
- Secure password generation (writes to file, not echoed)
- Executes via docker exec into mariadb container
- Proper SQL escaping
"""

import argparse
import os
import secrets
import subprocess
import sys
from pathlib import Path


class DatabaseManager:
    """Manages MariaDB operations via docker exec."""

    def __init__(self, container_name: str = "mariadb", base_dir: str = "/app"):
        self.container_name = container_name
        self.base_dir = Path(base_dir)
        self.password_file = self.base_dir / ".generated_passwords"

    def _docker_exec(self, cmd: list[str], interactive: bool = False) -> tuple[int, str, str]:
        """Execute command in docker container."""
        docker_cmd = ["docker", "exec"]
        if interactive:
            docker_cmd.extend(["-it"])
        docker_cmd.extend([self.container_name])
        docker_cmd.extend(cmd)

        try:
            result = subprocess.run(docker_cmd, capture_output=not interactive, text=True)
            return result.returncode, result.stdout or "", result.stderr or ""
        except Exception as e:
            return 1, "", str(e)

    def _mysql_exec(self, sql: str, needs_password: bool = True) -> tuple[int, str, str]:
        """Execute SQL via mysql client in container."""
        cmd = ["mysql"]
        if needs_password:
            cmd.append("-p")
        cmd.extend(["-e", sql])
        return self._docker_exec(cmd)

    def generate_password(self, length: int = 32) -> str:
        """Generate a secure random password."""
        return secrets.token_hex(length // 2)

    def save_password(self, username: str, password: str) -> Path:
        """Save generated password to file."""
        # Save to a per-user file for security
        password_file = self.base_dir / "etc" / ".db_passwords" / f"{username}.txt"
        password_file.parent.mkdir(parents=True, exist_ok=True)

        with open(password_file, "w") as f:
            f.write(f"Username: {username}\n")
            f.write(f"Password: {password}\n")

        # Secure permissions
        os.chmod(password_file, 0o600)

        return password_file

    def console(self) -> int:
        """Open interactive MySQL console."""
        print(f"Connecting to {self.container_name}...")
        return self._docker_exec(["mysql", "-p"], interactive=True)[0]

    def list_databases(self) -> tuple[int, list[str]]:
        """List all databases."""
        code, stdout, stderr = self._mysql_exec("SHOW DATABASES;")
        if code != 0:
            print(f"Error: {stderr}", file=sys.stderr)
            return code, []

        # Parse output (skip header line)
        databases = [line.strip() for line in stdout.strip().split("\n")[1:] if line.strip()]
        return 0, databases

    def list_users(self) -> tuple[int, list[str]]:
        """List all database users."""
        code, stdout, stderr = self._mysql_exec("SELECT User, Host FROM mysql.user;")
        if code != 0:
            print(f"Error: {stderr}", file=sys.stderr)
            return code, []

        users = [line.strip() for line in stdout.strip().split("\n")[1:] if line.strip()]
        return 0, users

    def create_database(self, dbname: str) -> int:
        """Create a database."""
        sql = f"CREATE DATABASE IF NOT EXISTS `{dbname}`;"
        code, stdout, stderr = self._mysql_exec(sql)
        if code != 0:
            print(f"Error creating database: {stderr}", file=sys.stderr)
        else:
            print(f"Database '{dbname}' created successfully")
        return code

    def create_user(self, username: str, password: str | None = None, generate: bool = False) -> tuple[int, str | None]:
        """Create a database user. Returns (exit_code, password_if_generated)."""
        if generate:
            password = self.generate_password()
        elif not password:
            print("Error: Either --password or --generate required", file=sys.stderr)
            return 1, None

        sql = f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{password}';"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            print(f"Error creating user: {stderr}", file=sys.stderr)
            return code, None

        if generate:
            password_file = self.save_password(username, password)
            print(f"User '{username}' created successfully")
            print(f"Password saved to: {password_file}")
            return 0, password
        else:
            print(f"User '{username}' created successfully")
            return 0, None

    def grant_privileges(self, dbname: str, username: str) -> int:
        """Grant all privileges on a database to a user."""
        sql = f"GRANT ALL PRIVILEGES ON `{dbname}`.* TO '{username}'@'%';"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            print(f"Error granting privileges: {stderr}", file=sys.stderr)
        else:
            print(f"Granted all privileges on '{dbname}' to '{username}'")

        # Flush privileges
        self._mysql_exec("FLUSH PRIVILEGES;")
        return code

    def remove_user(self, username: str) -> int:
        """Remove a database user."""
        sql = f"DROP USER IF EXISTS '{username}'@'%';"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            print(f"Error removing user: {stderr}", file=sys.stderr)
        else:
            print(f"User '{username}' removed")
        return code

    def drop_database(self, dbname: str) -> int:
        """Drop a database."""
        sql = f"DROP DATABASE IF EXISTS `{dbname}`;"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            print(f"Error dropping database: {stderr}", file=sys.stderr)
        else:
            print(f"Database '{dbname}' dropped")
        return code

    def setup(self, name: str) -> int:
        """Create user with generated password, database, and grant privileges."""
        print(f"Setting up database and user for '{name}'...")

        # Create user with generated password
        code, password = self.create_user(name, generate=True)
        if code != 0:
            return code

        # Create database
        code = self.create_database(name)
        if code != 0:
            return code

        # Grant privileges
        code = self.grant_privileges(name, name)
        if code != 0:
            return code

        print(f"\nSetup complete for '{name}'")
        print(f"Add the following to your service's .env file:")
        print(f"  DB_USER={name}")
        print(f"  DB_NAME={name}")
        print(f"  DB_PASSWORD=<see password file>")
        return 0


def main():
    parser = argparse.ArgumentParser(
        description="Database helper operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  database.py console                    # Open interactive MySQL console
  database.py list-databases             # Show all databases
  database.py list-users                 # Show all users
  database.py create-db myapp            # Create database 'myapp'
  database.py create-user myapp --generate  # Create user with generated password
  database.py grant myapp myapp          # Grant privileges
  database.py setup myapp                # All-in-one: user + db + grant
        """,
    )

    parser.add_argument(
        "action",
        choices=["console", "list-databases", "list-users", "create-db", "create-user", "grant", "remove-user", "drop-db", "setup"],
        help="Action to perform",
    )
    parser.add_argument("args", nargs="*", help="Arguments for the action")
    parser.add_argument("--password", "-p", help="Password for create-user")
    parser.add_argument("--generate", "-g", action="store_true", help="Generate password for create-user")
    parser.add_argument("--container", "-c", default="mariadb", help="Container name (default: mariadb)")
    parser.add_argument("--base-dir", default="/app", help="Base directory (default: /app)")

    args = parser.parse_args()
    mgr = DatabaseManager(container_name=args.container, base_dir=args.base_dir)

    if args.action == "console":
        return mgr.console()

    if args.action == "list-databases":
        code, databases = mgr.list_databases()
        if code == 0:
            for db in databases:
                print(db)
        return code

    if args.action == "list-users":
        code, users = mgr.list_users()
        if code == 0:
            for user in users:
                print(user)
        return code

    if args.action == "create-db":
        if not args.args:
            parser.error("Database name required")
        return mgr.create_database(args.args[0])

    if args.action == "create-user":
        if not args.args:
            parser.error("Username required")
        code, _ = mgr.create_user(args.args[0], password=args.password, generate=args.generate)
        return code

    if args.action == "grant":
        if len(args.args) < 2:
            parser.error("Database and username required: grant <db> <user>")
        return mgr.grant_privileges(args.args[0], args.args[1])

    if args.action == "remove-user":
        if not args.args:
            parser.error("Username required")
        return mgr.remove_user(args.args[0])

    if args.action == "drop-db":
        if not args.args:
            parser.error("Database name required")
        return mgr.drop_database(args.args[0])

    if args.action == "setup":
        if not args.args:
            parser.error("Name required for setup")
        return mgr.setup(args.args[0])

    return 0


if __name__ == "__main__":
    sys.exit(main())
