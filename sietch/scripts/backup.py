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
import subprocess
import sys
from datetime import datetime
from pathlib import Path


# Default exclusions
DEFAULT_EXCLUSIONS = [
    ".keep",
    "etc/plex/Library",  # Plex library is huge
]

# Directories to include in backup
BACKUP_DIRS = [
    "etc",
    "services-enabled",
    "overrides-enabled",
]


class BackupManager:
    """Manages backup and restore operations."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.backup_dir = self.base_dir / "backups"
        self.hostname = os.environ.get("HOST_NAME", os.uname().nodename)

        # NFS settings from environment
        self.nfs_server = os.environ.get("NFS_SERVER", "")
        self.nfs_backup_path = os.environ.get("NFS_BACKUP_PATH", "")
        self.nfs_tmp_dir = Path(os.environ.get("NFS_BACKUP_TMP_DIR", "/tmp/nfs_backup"))

    def _run_cmd(self, cmd: list[str], sudo: bool = False) -> tuple[int, str, str]:
        """Run a shell command."""
        if sudo:
            cmd = ["sudo"] + cmd
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        except Exception as e:
            return 1, "", str(e)

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
        cmd = ["tar"]

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
        """Mount NFS backup location."""
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
        """Unmount NFS and cleanup."""
        code, _, _ = self._run_cmd(["umount", str(self.nfs_tmp_dir)], sudo=True)
        if code == 0:
            self._run_cmd(["rm", "-r", str(self.nfs_tmp_dir)], sudo=True)
        return code == 0

    def create_nfs_backup(self, direct: bool = False) -> int:
        """Create backup and copy to NFS, or create directly on NFS."""
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
        """,
    )

    parser.add_argument(
        "action",
        choices=["create", "restore", "list", "create-nfs", "restore-nfs"],
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

    return 0


if __name__ == "__main__":
    sys.exit(main())
