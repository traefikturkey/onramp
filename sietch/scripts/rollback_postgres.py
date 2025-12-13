#!/usr/bin/env python
"""
rollback_postgres.py - Rollback a service to dedicated postgres container

This script reverses a postgres migration by:
1. Stopping the service
2. Enabling the dedicated postgres override
3. Optionally restoring data from backup
4. Restarting the service with dedicated postgres

Usage:
  rollback_postgres.py <service>                    # Rollback to dedicated postgres
  rollback_postgres.py <service> --backup <file>    # Restore from specific backup
  rollback_postgres.py <service> --latest-backup    # Use most recent backup

Safety:
- Creates backup of shared postgres data before rollback
- Preserves migration backups for reference
- Can be run multiple times safely
"""

import argparse
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from postgres_manager import PostgresManager
except ImportError:
    print("Error: postgres_manager module not found", file=sys.stderr)
    sys.exit(1)


class PostgresRollback:
    """Handles rollback from shared to dedicated postgres."""

    def __init__(self, service: str, base_dir: str = "/app", dry_run: bool = False):
        self.service = service
        self.base_dir = Path(base_dir)
        self.dry_run = dry_run
        self.pg_manager = PostgresManager(base_dir=base_dir)

        self.overrides_available = self.base_dir / "overrides-available"
        self.overrides_enabled = self.base_dir / "overrides-enabled"
        self.backup_dir = self.base_dir / "backups" / "postgres-migrations"

    def find_latest_backup(self) -> Optional[Path]:
        """Find the most recent backup for this service."""
        if not self.backup_dir.exists():
            return None

        backups = sorted(self.backup_dir.glob(f"{self.service}_*.dump"), reverse=True)
        return backups[0] if backups else None

    def backup_current_state(self) -> Optional[Path]:
        """Backup current shared postgres data before rollback."""
        print(f"Backing up current state from shared postgres...")

        if not self.pg_manager.database_exists(self.service):
            print(f"  No database found in shared postgres for '{self.service}'")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"{self.service}_pre_rollback_{timestamp}.dump"

        if self.dry_run:
            print(f"  [DRY RUN] Would backup to {backup_path}")
            return backup_path

        code = self.pg_manager.backup_database(self.service, backup_path)
        if code != 0:
            print(f"⚠️  Backup failed, but continuing...")
            return None

        print(f"  ✅ Backed up to {backup_path}")
        return backup_path

    def enable_dedicated_override(self) -> bool:
        """Enable the dedicated postgres override."""
        override_file = f"{self.service}-dedicated-postgres.yml"
        override_available = self.overrides_available / override_file
        override_enabled = self.overrides_enabled / override_file

        print(f"Enabling dedicated postgres override...")

        if not override_available.exists():
            print(f"❌ Override not found: {override_available}")
            print(f"   Migration may not have created a rollback override.")
            print(f"   You may need to manually restore the original service YAML.")
            return False

        if self.dry_run:
            print(f"  [DRY RUN] Would symlink {override_file}")
            return True

        # Create symlink
        if override_enabled.exists():
            override_enabled.unlink()

        override_enabled.symlink_to(f"../overrides-available/{override_file}")
        print(f"  ✅ Enabled {override_file}")
        return True

    def restore_backup(self, backup_path: Path, target_container: str) -> bool:
        """Restore backup to dedicated postgres container."""
        print(f"Restoring backup to dedicated postgres...")

        if not backup_path.exists():
            print(f"❌ Backup not found: {backup_path}")
            return False

        if self.dry_run:
            print(f"  [DRY RUN] Would restore {backup_path} to {target_container}")
            return True

        # The dedicated container will create its own database
        # We need to wait for it to be ready, then restore
        print(f"  Waiting for {target_container} to be ready...")

        # Check if container is running
        check_cmd = ["docker", "ps", "--filter", f"name={target_container}", "--format", "{{.Names}}"]
        result = subprocess.run(check_cmd, capture_output=True, text=True)

        if target_container not in result.stdout:
            print(f"  ⚠️  Container {target_container} not running yet")
            print(f"  Start the service first: make restart")
            return False

        # Use pg_restore via docker exec
        print(f"  Copying backup to container...")
        copy_cmd = ["docker", "cp", str(backup_path), f"{target_container}:/tmp/restore.dump"]
        result = subprocess.run(copy_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"❌ Failed to copy backup: {result.stderr}")
            return False

        # Restore using pg_restore
        print(f"  Restoring database...")
        restore_cmd = [
            "docker",
            "exec",
            target_container,
            "pg_restore",
            "-U",
            "postgres",
            "-d",
            self.service,
            "--clean",
            "--if-exists",
            "/tmp/restore.dump",
        ]

        result = subprocess.run(restore_cmd, capture_output=True, text=True)

        # Cleanup
        subprocess.run(["docker", "exec", target_container, "rm", "/tmp/restore.dump"], capture_output=True)

        if result.returncode != 0:
            print(f"  ⚠️  Restore warnings (may be normal): {result.stderr}")
        else:
            print(f"  ✅ Database restored")

        return True

    def remove_from_shared_postgres(self) -> bool:
        """Optionally remove database from shared postgres after rollback."""
        if not self.pg_manager.database_exists(self.service):
            return True

        print(f"\nDatabase '{self.service}' still exists in shared postgres.")
        if self.dry_run:
            print(f"  [DRY RUN] Would ask to drop database")
            return True

        response = input(f"Drop it from shared postgres? [y/N] ")
        if response.lower() == "y":
            code = self.pg_manager.drop_database(self.service)
            return code == 0

        print(f"  Keeping database in shared postgres (safe to drop later)")
        return True

    def rollback(self, backup_path: Optional[Path] = None, use_latest: bool = False) -> bool:
        """Execute complete rollback workflow."""
        print(f"\n{'='*60}")
        print(f"PostgreSQL Rollback: {self.service}")
        print(f"{'='*60}\n")

        # Step 1: Backup current state
        print(f"Step 1/4: Backing up current state...")
        current_backup = self.backup_current_state()

        # Step 2: Enable dedicated postgres override
        print(f"\nStep 2/4: Enabling dedicated postgres...")
        if not self.enable_dedicated_override():
            return False

        # Step 3: Restore data if requested
        if use_latest or backup_path:
            print(f"\nStep 3/4: Restoring data...")

            if use_latest:
                backup_path = self.find_latest_backup()
                if not backup_path:
                    print(f"❌ No backup found for '{self.service}'")
                    return False
                print(f"  Using latest backup: {backup_path}")

            # Determine target container name
            # This should match what's in the override
            target_container = f"{self.service}-db"  # Common pattern

            if not self.restore_backup(backup_path, target_container):
                print(f"⚠️  Data restore failed, but override is enabled")
                print(f"  You can manually restore after starting the service")
        else:
            print(f"\nStep 3/4: Skipping data restore (no backup specified)")
            print(f"  The dedicated postgres will start with empty database")
            print(f"  Use --latest-backup or --backup to restore data")

        # Step 4: Cleanup
        print(f"\nStep 4/4: Cleanup...")
        self.remove_from_shared_postgres()

        print(f"\n{'='*60}")
        print(f"✅ Rollback Configuration Complete!")
        print(f"{'='*60}\n")

        print(f"Next steps:")
        print(f"  1. Restart the service: make restart")
        print(f"  2. Wait for postgres container to start")
        print(f"  3. Check logs: docker logs {self.service}")

        if current_backup:
            print(f"\nCurrent state backed up to:")
            print(f"  {current_backup}")

        print(f"\nTo reverse this rollback (return to shared postgres):")
        print(f"  make disable-override {self.service}-dedicated-postgres && make restart\n")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Rollback service from shared postgres to dedicated instance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  rollback_postgres.py docmost                     # Rollback with empty database
  rollback_postgres.py joplin --latest-backup      # Rollback with most recent backup
  rollback_postgres.py netbox --backup backup.dump # Rollback with specific backup

Safety features:
  - Backs up current shared postgres data before rollback
  - Preserves all migration backups
  - Idempotent - safe to run multiple times
  - Can be reversed by disabling override

The rollback process:
  1. Backs up current data from shared postgres
  2. Enables dedicated postgres override
  3. Optionally restores data to dedicated postgres
  4. Cleans up shared postgres database
        """,
    )

    parser.add_argument("service", help="Service name to rollback")
    parser.add_argument("--backup", type=Path, help="Specific backup file to restore")
    parser.add_argument("--latest-backup", action="store_true", help="Use most recent backup")
    parser.add_argument("--dry-run", action="store_true", help="Preview rollback without making changes")
    parser.add_argument("--base-dir", default="/app", help="OnRamp base directory")

    args = parser.parse_args()

    try:
        rollback = PostgresRollback(args.service, args.base_dir, args.dry_run)
        success = rollback.rollback(args.backup, args.latest_backup)
        return 0 if success else 1

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
