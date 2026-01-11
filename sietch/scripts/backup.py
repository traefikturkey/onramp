#!/usr/bin/env python
"""
backup.py - Backup and restore operations for OnRamp

Commands:
  create [--service <name>] [--exclude <pattern>]...
  restore [--file <path> | --latest] [--service <name>]
  list [--location local|nfs]
  create-nfs [--direct]
  restore-nfs

Features:
- Structured exclusion list
- Progress indication for large backups
- NFS mount handling with proper error recovery
- Backup listing and discovery
"""

import argparse
import fnmatch
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.command import CommandExecutor


# Default exclusions - patterns to skip during backup
# These reduce backup size by excluding regeneratable/non-essential data
DEFAULT_EXCLUSIONS = [
    # Placeholder files
    ".keep",
    ".gitkeep",
    # Plex library (huge, regeneratable)
    "etc/plex/Library",
    # Log files
    "*.log",
    "logs/",
    "Logs/",
    # Cache directories
    "cache/",
    "Cache/",
    ".cache/",
    "__pycache__/",
    # Git pack files (large, regeneratable from repo)
    ".git/objects/pack/",
    # Large binary artifacts
    "*.iso",
    "*.img",
    "*.qcow2",
    # AI model files (huge, downloadable)
    "*.safetensors",
    "*.gguf",
    "pytorch_model.bin",
    "*.partial",
    # Game server binaries (downloadable)
    "etc/games/",
    # Database files (should be backed up separately via dump)
    "etc/*/db/journal/",
    # Temporary files
    "tmp/",
    "temp/",
    "*.tmp",
    "*.swp",
]

# Directories to include in backup
BACKUP_DIRS = [
    "etc",
    "services-enabled",
    "overrides-enabled",
    "external-enabled",
]


class BackupManager:
    """Manages backup and restore operations."""

    def __init__(
        self,
        base_dir: str = "/app",
        executor: "CommandExecutor | None" = None,
    ):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self.hostname = os.environ.get("HOST_NAME", "unknown")

        # NFS settings from environment
        self.nfs_server = os.environ.get("NFS_SERVER", "")
        self.nfs_backup_path = os.environ.get("NFS_BACKUP_PATH", "")
        self.nfs_tmp_dir = Path(os.environ.get("NFS_BACKUP_TMP_DIR", "/tmp/nfs_backup"))

        # Pre-mount detection: when using Docker NFS volume, mount is already done
        self.nfs_premounted = os.environ.get("NFS_PREMOUNTED", "").lower() == "true"

        # Use injected executor or create default
        if executor is not None:
            self._executor = executor
        else:
            from adapters.subprocess_cmd import SubprocessCommandExecutor

            self._executor = SubprocessCommandExecutor()

    def _run_cmd(self, cmd: list[str], sudo: bool = False) -> tuple[int, str, str]:
        """Run a shell command."""
        if sudo:
            # Try with sudo first, fall back to direct execution if sudo not available
            result = self._executor.run(["sudo"] + cmd)
            # Check if sudo not found (error message or exit code)
            if result.returncode != 0 and "sudo" in result.stderr.lower():
                result = self._executor.run(cmd)
        else:
            result = self._executor.run(cmd)
        return result.returncode, result.stdout, result.stderr

    def ensure_backup_dir(self) -> bool:
        """Ensure backup directory exists."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        return True

    def generate_backup_name(self, service: str | None = None) -> str:
        """Generate backup filename with timestamp."""
        timestamp = datetime.now().strftime("%y-%m-%d-%H%M")
        if service:
            return f"onramp-config-backup-{self.hostname}-{service}-{timestamp}.tar.gz"
        return f"onramp-config-backup-{self.hostname}-{timestamp}.tar.gz"

    def list_backups(self, location: str = "local") -> list[dict]:
        """List available backups."""
        backups = []

        if location == "local":
            backup_path = self.backup_dir
        elif location == "nfs":
            if not self._mount_nfs():
                return []
            backup_path = self.nfs_tmp_dir
        else:
            return []

        if not backup_path.exists():
            return []

        for f in backup_path.glob(f"*{self.hostname}*.tar.gz"):
            stat = f.stat()
            backups.append(
                {
                    "name": f.name,
                    "path": str(f),
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                }
            )

        # Sort by modification time, newest first
        backups.sort(key=lambda x: x["modified"], reverse=True)

        if location == "nfs":
            self._unmount_nfs()

        return backups

    def find_latest_backup(self, service: str | None = None, location: str = "local") -> str | None:
        """Find the most recent backup file."""
        backups = self.list_backups(location)

        if service:
            # Filter to service-specific backups
            backups = [b for b in backups if f"-{service}-" in b["name"]]

        if backups:
            return backups[0]["path"]
        return None

    def create_backup(
        self, service: str | None = None, exclusions: list[str] | None = None, output_dir: Path | None = None
    ) -> tuple[int, str | None]:
        """Create a backup. Returns (exit_code, backup_path)."""
        self.ensure_backup_dir()

        if output_dir is None:
            output_dir = self.backup_dir

        backup_name = self.generate_backup_name(service)
        backup_path = output_dir / backup_name

        # Build exclusion list
        all_exclusions = DEFAULT_EXCLUSIONS.copy()
        if exclusions:
            all_exclusions.extend(exclusions)

        # Add exclusions from environment
        env_exclusions = os.environ.get("ONRAMP_BACKUP_EXCLUSIONS", "")
        if env_exclusions:
            all_exclusions.extend(env_exclusions.split())

        # Build tar command
        # --ignore-failed-read: continue past permission errors (some service dirs are owned by other users)
        # --warning=no-file-changed: suppress warnings about files modified during backup
        cmd = ["tar", "--ignore-failed-read", "--warning=no-file-changed"]

        # Add exclusions
        for excl in all_exclusions:
            cmd.extend(["--exclude", excl])

        cmd.extend(["-czf", str(backup_path)])

        # Add directories to backup
        if service:
            # Service-specific backup
            service_etc = self.base_dir / "etc" / service
            if not service_etc.exists():
                print(f"Error: Service directory not found: {service_etc}", file=sys.stderr)
                return 1, None
            cmd.append(f"./etc/{service}")
        else:
            # Full backup
            for dir_name in BACKUP_DIRS:
                dir_path = self.base_dir / dir_name
                if dir_path.exists():
                    cmd.append(f"./{dir_name}")

            # Add inclusions from environment
            env_inclusions = os.environ.get("ONRAMP_BACKUP_INCLUSIONS", "")
            if env_inclusions:
                cmd.extend(env_inclusions.split())

        print(f"Creating backup: {backup_name}")
        print(f"  Directories: {' '.join(cmd[cmd.index('-czf') + 2 :])}")

        # Run from base directory
        code, stdout, stderr = self._run_cmd(cmd, sudo=True)

        if code != 0:
            print(f"Error creating backup: {stderr}", file=sys.stderr)
            return code, None

        # Get file size
        if backup_path.exists():
            size_mb = backup_path.stat().st_size / (1024 * 1024)
            print(f"  Created: {backup_path} ({size_mb:.1f} MB)")

        return 0, str(backup_path)

    def restore_backup(self, backup_path: str | None = None, service: str | None = None) -> int:
        """Restore from a backup file."""
        if backup_path is None:
            backup_path = self.find_latest_backup(service)
            if not backup_path:
                print("Error: No backup file found", file=sys.stderr)
                return 1

        backup_file = Path(backup_path)
        if not backup_file.exists():
            print(f"Error: Backup file not found: {backup_path}", file=sys.stderr)
            return 1

        print(f"Restoring from: {backup_file.name}")

        cmd = ["tar", "-xvf", str(backup_file)]
        code, stdout, stderr = self._run_cmd(cmd, sudo=True)

        if code != 0:
            print(f"Error restoring backup: {stderr}", file=sys.stderr)
            return code

        print("Restore complete. Run 'make restart' to apply changes.")
        return 0

    def _mount_nfs(self) -> bool:
        """Mount NFS backup location.

        If NFS_PREMOUNTED=true (Docker NFS volume), skips mount and verifies path exists.
        Otherwise attempts runtime mount (requires root/sudo).
        """
        # Pre-mounted via Docker NFS volume - just verify path is accessible
        if self.nfs_premounted:
            if self.nfs_tmp_dir.exists() and self.nfs_tmp_dir.is_dir():
                return True
            print(f"Error: NFS_PREMOUNTED=true but {self.nfs_tmp_dir} not accessible", file=sys.stderr)
            return False

        # Runtime mount path - requires NFS_SERVER and NFS_BACKUP_PATH
        if not self.nfs_server or not self.nfs_backup_path:
            print("Error: NFS_SERVER and NFS_BACKUP_PATH must be set", file=sys.stderr)
            return False

        # Create mount point
        self._run_cmd(["mkdir", "-p", str(self.nfs_tmp_dir)], sudo=True)

        # Mount
        nfs_source = f"{self.nfs_server}:{self.nfs_backup_path}"
        code, _, stderr = self._run_cmd(["mount", "-t", "nfs", nfs_source, str(self.nfs_tmp_dir)], sudo=True)

        if code != 0:
            print(f"Error mounting NFS: {stderr}", file=sys.stderr)
            return False

        return True

    def _unmount_nfs(self) -> bool:
        """Unmount NFS and cleanup.

        If NFS_PREMOUNTED=true (Docker NFS volume), skips unmount - Docker handles it.
        """
        if self.nfs_premounted:
            return True  # Docker handles volume lifecycle

        code, _, _ = self._run_cmd(["umount", str(self.nfs_tmp_dir)], sudo=True)
        if code == 0:
            self._run_cmd(["rm", "-r", str(self.nfs_tmp_dir)], sudo=True)
        return code == 0

    def create_nfs_backup(self, direct: bool = False) -> int:
        """Create backup and copy to NFS, or create directly on NFS."""
        # Ensure mount point exists before attempting mount
        if not self.nfs_tmp_dir.exists():
            code, _, stderr = self._run_cmd(["mkdir", "-p", str(self.nfs_tmp_dir)], sudo=True)
            if code != 0:
                print(f"Error creating NFS mount point: {stderr}", file=sys.stderr)
                return 1

        if not self._mount_nfs():
            return 1

        try:
            if direct:
                # Create backup directly to NFS
                code, backup_path = self.create_backup(output_dir=self.nfs_tmp_dir)
            else:
                # Create locally, then move
                code, backup_path = self.create_backup()
                if code == 0 and backup_path:
                    # Move to NFS
                    self._run_cmd(["mv", backup_path, str(self.nfs_tmp_dir)], sudo=True)
                    print(f"Moved backup to NFS")
        finally:
            self._unmount_nfs()

        return code

    def restore_nfs_backup(self) -> int:
        """Restore latest backup from NFS."""
        if not self._mount_nfs():
            return 1

        try:
            # Find latest backup on NFS
            backup_path = self.find_latest_backup(location="nfs")
            if not backup_path:
                print("Error: No backup found on NFS", file=sys.stderr)
                return 1

            # Copy to local backups
            self.ensure_backup_dir()
            local_path = self.backup_dir / Path(backup_path).name
            self._run_cmd(["cp", "-p", backup_path, str(local_path)], sudo=False)

            # Restore
            return self.restore_backup(str(local_path))
        finally:
            self._unmount_nfs()

    def discover_database_containers(self) -> list[dict]:
        """Discover running database containers.

        Returns list of dicts with container info:
        - name: container name
        - type: 'postgres' or 'mariadb'
        - service: inferred service name
        """
        containers = []

        # Get list of running containers
        code, stdout, stderr = self._run_cmd(
            ["docker", "ps", "--format", "{{.Names}}"]
        )
        if code != 0:
            print(f"Error listing containers: {stderr}", file=sys.stderr)
            return containers

        for name in stdout.strip().split("\n"):
            if not name:
                continue

            # Check for PostgreSQL containers
            if "-db" in name or name in ("postgres",):
                # Check if it's PostgreSQL
                code, _, _ = self._run_cmd(
                    ["docker", "exec", name, "pg_isready", "-q"]
                )
                if code == 0:
                    service = name.replace("-db", "").replace("-postgres", "")
                    containers.append({
                        "name": name,
                        "type": "postgres",
                        "service": service,
                    })
                    continue

                # Check if it's MariaDB/MySQL
                code, _, _ = self._run_cmd(
                    ["docker", "exec", name, "mysqladmin", "ping", "-s"]
                )
                if code == 0:
                    service = name.replace("-db", "").replace("-mariadb", "").replace("-mysql", "")
                    containers.append({
                        "name": name,
                        "type": "mariadb",
                        "service": service,
                    })

            # Check standalone mariadb/mysql containers
            elif name in ("mariadb", "mysql"):
                containers.append({
                    "name": name,
                    "type": "mariadb",
                    "service": "shared",
                })

        return containers

    def dump_postgres(self, container: str, output_dir: Path) -> tuple[int, str | None]:
        """Dump all databases from a PostgreSQL container."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        dump_file = output_dir / f"{container}-{timestamp}.sql"

        print(f"  Dumping PostgreSQL: {container} -> {dump_file.name}")

        # Use pg_dumpall to get all databases
        code, stdout, stderr = self._run_cmd([
            "docker", "exec", container,
            "pg_dumpall", "-U", "postgres"
        ])

        if code != 0:
            # Try with 'admin' user (OnRamp default)
            code, stdout, stderr = self._run_cmd([
                "docker", "exec", container,
                "pg_dumpall", "-U", "admin"
            ])

        if code != 0:
            print(f"    Error: {stderr}", file=sys.stderr)
            return code, None

        # Write dump to file
        with open(dump_file, "w") as f:
            f.write(stdout)

        size_mb = dump_file.stat().st_size / (1024 * 1024)
        print(f"    Created: {dump_file.name} ({size_mb:.1f} MB)")
        return 0, str(dump_file)

    def dump_mariadb(self, container: str, output_dir: Path) -> tuple[int, str | None]:
        """Dump all databases from a MariaDB container."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M")
        dump_file = output_dir / f"{container}-{timestamp}.sql"

        print(f"  Dumping MariaDB: {container} -> {dump_file.name}")

        # Use mysqldump with --all-databases
        code, stdout, stderr = self._run_cmd([
            "docker", "exec", container,
            "mysqldump", "--all-databases", "-u", "root"
        ])

        if code != 0:
            print(f"    Error: {stderr}", file=sys.stderr)
            return code, None

        # Write dump to file
        with open(dump_file, "w") as f:
            f.write(stdout)

        size_mb = dump_file.stat().st_size / (1024 * 1024)
        print(f"    Created: {dump_file.name} ({size_mb:.1f} MB)")
        return 0, str(dump_file)

    def dump_databases(self) -> int:
        """Dump all discovered database containers."""
        db_backup_dir = self.backup_dir / "databases"
        db_backup_dir.mkdir(parents=True, exist_ok=True)

        print("Discovering database containers...")
        containers = self.discover_database_containers()

        if not containers:
            print("No database containers found")
            return 0

        print(f"Found {len(containers)} database container(s)")
        success_count = 0
        error_count = 0

        for db in containers:
            if db["type"] == "postgres":
                code, _ = self.dump_postgres(db["name"], db_backup_dir)
            elif db["type"] == "mariadb":
                code, _ = self.dump_mariadb(db["name"], db_backup_dir)
            else:
                continue

            if code == 0:
                success_count += 1
            else:
                error_count += 1

        print(f"\nDatabase dump complete: {success_count} succeeded, {error_count} failed")
        return 1 if error_count > 0 else 0


def main():
    parser = argparse.ArgumentParser(
        description="Backup and restore operations",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  backup.py create                    # Create full backup
  backup.py create --service plex     # Backup only plex
  backup.py restore --latest          # Restore most recent backup
  backup.py restore --file backup.tar.gz
  backup.py list                      # List local backups
  backup.py list --location nfs       # List NFS backups
  backup.py create-nfs                # Create and copy to NFS
  backup.py create-nfs --direct       # Create directly on NFS
  backup.py restore-nfs               # Restore latest from NFS
  backup.py dump-databases            # Dump all database containers
        """,
    )

    parser.add_argument(
        "action",
        choices=["create", "restore", "list", "create-nfs", "restore-nfs", "dump-databases"],
        help="Action to perform",
    )
    parser.add_argument("--service", "-s", help="Service name (for service-specific backup)")
    parser.add_argument("--file", "-f", help="Specific backup file to restore")
    parser.add_argument("--latest", "-l", action="store_true", help="Use most recent backup")
    parser.add_argument("--exclude", "-e", action="append", help="Additional exclusion pattern")
    parser.add_argument("--location", choices=["local", "nfs"], default="local", help="Backup location for list")
    parser.add_argument("--direct", action="store_true", help="Create backup directly on NFS")
    parser.add_argument("--base-dir", default="/app", help="Base directory (default: /app)")

    args = parser.parse_args()

    # Change to base directory for relative paths in tar
    os.chdir(args.base_dir)

    mgr = BackupManager(args.base_dir)

    if args.action == "create":
        code, _ = mgr.create_backup(service=args.service, exclusions=args.exclude)
        return code

    if args.action == "restore":
        backup_file = args.file
        if args.latest or not backup_file:
            backup_file = mgr.find_latest_backup(service=args.service)
        return mgr.restore_backup(backup_file, service=args.service)

    if args.action == "list":
        backups = mgr.list_backups(location=args.location)
        if not backups:
            print(f"No backups found in {args.location}")
            return 0

        print(f"Backups in {args.location}:")
        for b in backups:
            size_mb = b["size"] / (1024 * 1024)
            date_str = b["modified"].strftime("%Y-%m-%d %H:%M")
            print(f"  {b['name']} ({size_mb:.1f} MB, {date_str})")
        return 0

    if args.action == "create-nfs":
        return mgr.create_nfs_backup(direct=args.direct)

    if args.action == "restore-nfs":
        return mgr.restore_nfs_backup()

    if args.action == "dump-databases":
        return mgr.dump_databases()

    return 0


if __name__ == "__main__":
    sys.exit(main())
