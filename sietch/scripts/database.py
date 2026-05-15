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
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from logging_config import get_logger, setup_logging

if TYPE_CHECKING:
    from ports.docker import DockerExecutor

logger = get_logger(__name__)


class DatabaseManager:
    """Manages MariaDB operations via docker exec."""

    def __init__(
        self,
        container_name: str = "mariadb",
        base_dir: str = "/app",
        docker: "DockerExecutor | None" = None,
    ):
        self.container_name = container_name
        self.base_dir = Path(base_dir)
        self.password_file = self.base_dir / ".generated_passwords"

        # Use injected docker executor or create default
        if docker is not None:
            self._docker = docker
        else:
            from adapters.docker_subprocess import SubprocessDockerExecutor

            self._docker = SubprocessDockerExecutor()

    def _docker_exec(self, cmd: list[str], interactive: bool = False) -> tuple[int, str, str]:
        """Execute command in docker container."""
        return self._docker.exec(self.container_name, cmd, interactive)

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
        logger.info("Connecting to database", extra={"container": self.container_name})
        return self._docker_exec(["mysql", "-p"], interactive=True)[0]

    def list_databases(self) -> tuple[int, list[str]]:
        """List all databases."""
        code, stdout, stderr = self._mysql_exec("SHOW DATABASES;")
        if code != 0:
            logger.error("Failed to list databases", extra={"stderr": stderr})
            return code, []

        # Parse output (skip header line)
        databases = [line.strip() for line in stdout.strip().split("\n")[1:] if line.strip()]
        return 0, databases

    def list_users(self) -> tuple[int, list[str]]:
        """List all database users."""
        code, stdout, stderr = self._mysql_exec("SELECT User, Host FROM mysql.user;")
        if code != 0:
            logger.error("Failed to list users", extra={"stderr": stderr})
            return code, []

        users = [line.strip() for line in stdout.strip().split("\n")[1:] if line.strip()]
        return 0, users

    def create_database(self, dbname: str) -> int:
        """Create a database."""
        sql = f"CREATE DATABASE IF NOT EXISTS `{dbname}`;"
        code, stdout, stderr = self._mysql_exec(sql)
        if code != 0:
            logger.error("Failed to create database", extra={"database": dbname, "stderr": stderr})
        else:
            logger.info("Database created successfully", extra={"database": dbname})
        return code

    def create_user(self, username: str, password: str | None = None, generate: bool = False) -> tuple[int, str | None]:
        """Create a database user. Returns (exit_code, password_if_generated)."""
        if generate:
            password = self.generate_password()
        elif not password:
            logger.error("Either --password or --generate required")
            return 1, None

        sql = f"CREATE USER IF NOT EXISTS '{username}'@'%' IDENTIFIED BY '{password}';"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            logger.error("Failed to create user", extra={"username": username, "stderr": stderr})
            return code, None

        if generate:
            password_file = self.save_password(username, password)
            logger.info("User created with generated password", extra={"username": username, "password_file": str(password_file)})
            return 0, password
        else:
            logger.info("User created successfully", extra={"username": username})
            return 0, None

    def grant_privileges(self, dbname: str, username: str) -> int:
        """Grant all privileges on a database to a user."""
        sql = f"GRANT ALL PRIVILEGES ON `{dbname}`.* TO '{username}'@'%';"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            logger.error("Failed to grant privileges", extra={"database": dbname, "username": username, "stderr": stderr})
        else:
            logger.info("Granted privileges", extra={"database": dbname, "username": username})

        # Flush privileges
        self._mysql_exec("FLUSH PRIVILEGES;")
        return code

    def remove_user(self, username: str) -> int:
        """Remove a database user."""
        sql = f"DROP USER IF EXISTS '{username}'@'%';"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            logger.error("Failed to remove user", extra={"username": username, "stderr": stderr})
        else:
            logger.info("User removed", extra={"username": username})
        return code

    def drop_database(self, dbname: str) -> int:
        """Drop a database."""
        sql = f"DROP DATABASE IF EXISTS `{dbname}`;"
        code, stdout, stderr = self._mysql_exec(sql)

        if code != 0:
            logger.error("Failed to drop database", extra={"database": dbname, "stderr": stderr})
        else:
            logger.info("Database dropped", extra={"database": dbname})
        return code

    def setup(self, name: str) -> int:
        """Create user with generated password, database, and grant privileges."""
        logger.info("Setting up database and user", extra={"name": name})

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

        logger.info("Setup complete", extra={"name": name})
        logger.info(f"Add to your service's .env file: DB_USER={name}, DB_NAME={name}, DB_PASSWORD=<see password file>")
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

    # Setup logging
    setup_logging(level="INFO", enable_colors=True)

    mgr = DatabaseManager(container_name=args.container, base_dir=args.base_dir)

    if args.action == "console":
        return mgr.console()

    if args.action == "list-databases":
        code, databases = mgr.list_databases()
        if code == 0:
            for db in databases:
                logger.info(db)
        return code

    if args.action == "list-users":
        code, users = mgr.list_users()
        if code == 0:
            for user in users:
                logger.info(user)
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
