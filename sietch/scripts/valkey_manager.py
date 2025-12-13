#!/usr/bin/env python
"""
valkey_manager.py - Valkey cache management for OnRamp

Commands:
  list-dbs                        - List all assigned database numbers
  assign-db <service>             - Assign next available database number to service
  get-db <service>                - Get assigned database number for service
  release-db <service>            - Release database assignment for service
  console [db]                    - Interactive valkey-cli console (optional db number)
  flush-db <db>                   - Flush specific database (careful!)
  info                            - Show Valkey server info
  ping                            - Test connection

Features:
- Executes via docker exec into valkey container
- Database assignments tracked in JSON file (0-15)
- Safe assignment with collision detection
- Persistent assignment tracking
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.docker import DockerExecutor


class ValkeyManager:
    """Manages Valkey operations via docker exec."""

    def __init__(
        self,
        container_name: str = "valkey",
        base_dir: str = "/app",
        docker: "DockerExecutor | None" = None,
    ):
        self.container_name = container_name
        self.base_dir = Path(base_dir)
        self.assignments_file = self.base_dir / "etc" / ".valkey_assignments.json"
        self.max_databases = 16  # Valkey/Redis supports 0-15

        if docker is not None:
            self._docker = docker
        else:
            from adapters.docker_subprocess import SubprocessDockerExecutor

            self._docker = SubprocessDockerExecutor()

    def _docker_exec(self, cmd: list[str], interactive: bool = False) -> tuple[int, str, str]:
        """Execute command in docker container."""
        return self._docker.exec(self.container_name, cmd, interactive)

    def _valkey_exec(self, *args: str) -> tuple[int, str, str]:
        """Execute valkey-cli command in container."""
        cmd = ["valkey-cli"] + list(args)
        return self._docker_exec(cmd)

    def _load_assignments(self) -> dict[str, int]:
        """Load database assignments from JSON file."""
        if not self.assignments_file.exists():
            return {}
        try:
            return json.loads(self.assignments_file.read_text())
        except json.JSONDecodeError:
            print(f"Warning: Corrupted assignments file, starting fresh", file=sys.stderr)
            return {}

    def _save_assignments(self, assignments: dict[str, int]) -> None:
        """Save database assignments to JSON file."""
        self.assignments_file.parent.mkdir(parents=True, exist_ok=True)
        self.assignments_file.write_text(json.dumps(assignments, indent=2, sort_keys=True))
        self.assignments_file.chmod(0o644)

    def ping(self) -> int:
        """Test connection to Valkey."""
        code, stdout, stderr = self._valkey_exec("ping")
        if code != 0:
            print(f"Error: {stderr}", file=sys.stderr)
        else:
            print(stdout.strip())
        return code

    def info(self) -> int:
        """Show Valkey server info."""
        code, stdout, stderr = self._valkey_exec("info")
        if code != 0:
            print(f"Error: {stderr}", file=sys.stderr)
        else:
            print(stdout)
        return code

    def console(self, db: int = 0) -> int:
        """Open interactive valkey-cli console."""
        print(f"Connecting to {self.container_name} (DB {db})...")
        return self._docker_exec(["valkey-cli", "-n", str(db)], interactive=True)[0]

    def list_databases(self) -> tuple[int, dict[str, int]]:
        """List all database assignments."""
        assignments = self._load_assignments()
        if not assignments:
            print("No database assignments found")
            return 0, {}

        print("\nValkey Database Assignments:")
        print("-" * 40)
        for service in sorted(assignments.keys()):
            db_num = assignments[service]
            print(f"  DB {db_num:2d}: {service}")
        print(f"\nTotal: {len(assignments)}/{self.max_databases} databases assigned")
        return 0, assignments

    def get_database(self, service: str) -> tuple[int, int | None]:
        """Get assigned database number for service."""
        assignments = self._load_assignments()
        db_num = assignments.get(service)
        
        if db_num is None:
            print(f"No database assigned to '{service}'", file=sys.stderr)
            return 1, None
        
        print(f"{service}: DB {db_num}")
        return 0, db_num

    def assign_database(self, service: str, preferred_db: int | None = None) -> tuple[int, int | None]:
        """Assign database number to service."""
        assignments = self._load_assignments()

        # Check if already assigned
        if service in assignments:
            db_num = assignments[service]
            print(f"Service '{service}' already has DB {db_num}")
            return 0, db_num

        # Use preferred database if specified and available
        if preferred_db is not None:
            if preferred_db < 0 or preferred_db >= self.max_databases:
                print(f"Error: Database number must be 0-{self.max_databases-1}", file=sys.stderr)
                return 1, None
            
            if preferred_db in assignments.values():
                assigned_to = [s for s, db in assignments.items() if db == preferred_db][0]
                print(f"Error: DB {preferred_db} already assigned to '{assigned_to}'", file=sys.stderr)
                return 1, None
            
            db_num = preferred_db
        else:
            # Find next available database
            used_dbs = set(assignments.values())
            available = [db for db in range(self.max_databases) if db not in used_dbs]
            
            if not available:
                print(f"Error: All {self.max_databases} databases are assigned", file=sys.stderr)
                return 1, None
            
            db_num = available[0]

        # Assign and save
        assignments[service] = db_num
        self._save_assignments(assignments)
        
        print(f"✅ Assigned DB {db_num} to '{service}'")
        return 0, db_num

    def release_database(self, service: str) -> int:
        """Release database assignment for service."""
        assignments = self._load_assignments()
        
        if service not in assignments:
            print(f"Service '{service}' has no database assignment", file=sys.stderr)
            return 1
        
        db_num = assignments.pop(service)
        self._save_assignments(assignments)
        
        print(f"Released DB {db_num} from '{service}'")
        return 0

    def flush_database(self, db: int) -> int:
        """Flush a specific database (removes all keys)."""
        if db < 0 or db >= self.max_databases:
            print(f"Error: Database number must be 0-{self.max_databases-1}", file=sys.stderr)
            return 1

        # Safety check - find what service uses this DB
        assignments = self._load_assignments()
        service = next((s for s, d in assignments.items() if d == db), None)
        
        if service:
            confirm = input(f"WARNING: DB {db} is assigned to '{service}'. Flush anyway? (yes/no): ")
            if confirm.lower() != "yes":
                print("Cancelled")
                return 1

        code, stdout, stderr = self._valkey_exec("-n", str(db), "FLUSHDB")
        if code != 0:
            print(f"Error: {stderr}", file=sys.stderr)
        else:
            print(f"✅ DB {db} flushed")
        return code


def main():
    parser = argparse.ArgumentParser(description="Manage Valkey cache databases")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # list-dbs
    subparsers.add_parser("list-dbs", help="List all database assignments")

    # assign-db <service> [--db N]
    assign_parser = subparsers.add_parser("assign-db", help="Assign database to service")
    assign_parser.add_argument("service", help="Service name")
    assign_parser.add_argument("--db", type=int, help="Preferred database number (0-15)")

    # get-db <service>
    get_parser = subparsers.add_parser("get-db", help="Get database number for service")
    get_parser.add_argument("service", help="Service name")

    # release-db <service>
    release_parser = subparsers.add_parser("release-db", help="Release database assignment")
    release_parser.add_argument("service", help="Service name")

    # console [db]
    console_parser = subparsers.add_parser("console", help="Open interactive console")
    console_parser.add_argument("db", nargs="?", type=int, default=0, help="Database number (default: 0)")

    # flush-db <db>
    flush_parser = subparsers.add_parser("flush-db", help="Flush database (removes all keys)")
    flush_parser.add_argument("db", type=int, help="Database number to flush")

    # info
    subparsers.add_parser("info", help="Show Valkey server info")

    # ping
    subparsers.add_parser("ping", help="Test connection")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    manager = ValkeyManager()

    try:
        if args.command == "list-dbs":
            code, _ = manager.list_databases()
        elif args.command == "assign-db":
            code, _ = manager.assign_database(args.service, args.db)
        elif args.command == "get-db":
            code, _ = manager.get_database(args.service)
        elif args.command == "release-db":
            code = manager.release_database(args.service)
        elif args.command == "console":
            code = manager.console(args.db)
        elif args.command == "flush-db":
            code = manager.flush_database(args.db)
        elif args.command == "info":
            code = manager.info()
        elif args.command == "ping":
            code = manager.ping()
        else:
            parser.print_help()
            code = 1

        return code

    except KeyboardInterrupt:
        print("\nInterrupted", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
