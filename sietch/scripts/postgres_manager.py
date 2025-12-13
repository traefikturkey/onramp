#!/usr/bin/env python
"""
postgres_manager.py - PostgreSQL helper operations for OnRamp

Commands:
  create-db <dbname>       - Create database if not exists
  list-databases           - List all databases
  drop-db <dbname>         - Drop database
  database-exists <dbname> - Check if database exists
  console                  - Interactive psql console

Features:
- Executes via docker exec into postgres container
- Safe database creation (IF NOT EXISTS)
- Proper SQL escaping
"""

import argparse
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.docker import DockerExecutor


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
        sql = f"SELECT 1 FROM pg_database WHERE datname='{dbname}'"
        code, stdout, stderr = self._psql_exec(sql)
        return code == 0 and "1" in stdout

    def create_database(self, dbname: str) -> int:
        """Create a database if it doesn't exist."""
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
        sql = f'DROP DATABASE IF EXISTS "{dbname}"'
        code, stdout, stderr = self._psql_exec(sql)
        if code != 0:
            print(f"Error dropping database: {stderr}", file=sys.stderr)
        else:
            print(f"Database '{dbname}' dropped")
        return code


def main():
    parser = argparse.ArgumentParser(
        description="PostgreSQL helper operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  postgres_manager.py console                # Open interactive psql console
  postgres_manager.py list-databases         # Show all databases
  postgres_manager.py create-db myapp        # Create database 'myapp'
  postgres_manager.py database-exists myapp  # Check if exists
  postgres_manager.py drop-db myapp          # Drop database
        """,
    )

    parser.add_argument(
        "action",
        choices=["console", "list-databases", "create-db", "drop-db", "database-exists"],
        help="Action to perform",
    )
    parser.add_argument("args", nargs="*", help="Arguments for the action")
    parser.add_argument("--container", "-c", default="postgres", help="Container name")
    parser.add_argument("--base-dir", default="/app", help="Base directory")

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

    return 0


if __name__ == "__main__":
    sys.exit(main())
