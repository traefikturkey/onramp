#!/usr/bin/env python
"""
migrate_service_env.py - Handle breaking environment variable changes for services

When services are migrated to new container images with different env var formats,
this script transforms existing env files to the new format.

Migrations are versioned and tracked to ensure they only run once.
"""

import argparse
import json
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Callable

# Migration registry: service -> list of migrations
# Each migration has: version, description, transform function
SERVICE_MIGRATIONS: dict[str, list[dict]] = {
    "samba": [
        {
            "version": 1,
            "description": "dperson/samba -> ghcr.io/servercontainers/samba",
            "image_change": "dperson/samba -> ghcr.io/servercontainers/samba",
            "transforms": {
                # Old format used USER=username;password, new uses ACCOUNT_username=password
                # Old format used SHARE=name;path;..., new uses SAMBA_VOLUME_CONFIG_name=[name]; path=...
                # We'll add new vars and comment out old ones
            },
            "notes": [
                "New image uses different env var format:",
                "  Old: USER=username;password",
                "  New: ACCOUNT_username=password, UID_username=1000",
                "  Old: SHARE=name;path;browsable;readonly;guest;users;admins;writers;comment",
                "  New: SAMBA_VOLUME_CONFIG_name=[name]; path=/path; writable=yes; ...",
                "Review and update your samba.env manually for complex configurations.",
            ],
        }
    ],
    "cloudflare-ddns": [
        {
            "version": 1,
            "description": "oznu/cloudflare-ddns -> ghcr.io/favonia/cloudflare-ddns",
            "image_change": "oznu/cloudflare-ddns -> ghcr.io/favonia/cloudflare-ddns",
            "transforms": {
                # Direct renames - old var -> new var
                "API_KEY": "CLOUDFLARE_API_TOKEN",
                # EMAIL is no longer needed with API token auth
                # ZONE + SUBDOMAIN -> DOMAINS (combined)
            },
            "notes": [
                "New image uses different env var format:",
                "  Old: API_KEY, EMAIL, ZONE, SUBDOMAIN",
                "  New: CLOUDFLARE_API_TOKEN, DOMAINS",
                "The DOMAINS var combines ZONE and SUBDOMAIN: ${SUBDOMAIN}.${ZONE}",
                "EMAIL is no longer needed when using API token.",
            ],
        }
    ],
    "unbound": [
        {
            "version": 1,
            "description": "mvance/unbound -> ghcr.io/pascaliske/unbound",
            "image_change": "mvance/unbound -> ghcr.io/pascaliske/unbound",
            "transforms": {},
            "notes": [
                "Image migrated to ghcr.io/pascaliske/unbound",
                "Environment variables are compatible - no changes needed.",
            ],
        }
    ],
}


class ServiceEnvMigrator:
    """Handles service-specific environment variable migrations."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.services_enabled = self.base_dir / "services-enabled"
        self.backups_dir = self.base_dir / "backups"
        self.state_file = self.base_dir / "etc" / ".service_migrations.json"

    def load_state(self) -> dict:
        """Load migration state from file."""
        if self.state_file.exists():
            return json.loads(self.state_file.read_text())
        return {"applied": {}}

    def save_state(self, state: dict) -> None:
        """Save migration state to file."""
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.write_text(json.dumps(state, indent=2))

    def get_applied_version(self, service: str) -> int:
        """Get the latest applied migration version for a service."""
        state = self.load_state()
        return state.get("applied", {}).get(service, 0)

    def set_applied_version(self, service: str, version: int) -> None:
        """Mark a migration version as applied."""
        state = self.load_state()
        if "applied" not in state:
            state["applied"] = {}
        state["applied"][service] = version
        state.setdefault("history", []).append({
            "service": service,
            "version": version,
            "timestamp": datetime.now().isoformat(),
        })
        self.save_state(state)

    def get_env_file(self, service: str) -> Path:
        """Get the env file path for a service."""
        return self.services_enabled / f"{service}.env"

    def parse_env_file(self, path: Path) -> list[tuple[str, str | None, str]]:
        """
        Parse env file preserving structure.
        Returns list of (line_type, var_name, content) tuples.
        line_type: 'comment', 'empty', 'var'
        """
        lines = []
        if not path.exists():
            return lines

        with open(path) as f:
            for line in f:
                line = line.rstrip("\n\r")
                if not line:
                    lines.append(("empty", None, ""))
                elif line.startswith("#"):
                    lines.append(("comment", None, line))
                else:
                    match = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line)
                    if match:
                        var_name, value = match.groups()
                        lines.append(("var", var_name, value))
                    else:
                        lines.append(("comment", None, line))
        return lines

    def write_env_file(self, path: Path, lines: list[tuple[str, str | None, str]]) -> None:
        """Write parsed lines back to env file."""
        with open(path, "w") as f:
            for line_type, var_name, content in lines:
                if line_type == "empty":
                    f.write("\n")
                elif line_type == "comment":
                    f.write(content + "\n")
                elif line_type == "var":
                    f.write(f"{var_name}={content}\n")

    def backup_env_file(self, service: str) -> Path | None:
        """Create a backup of the service env file."""
        env_file = self.get_env_file(service)
        if not env_file.exists():
            return None

        self.backups_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backups_dir / f"{service}.env.pre-migration-v{timestamp}"
        shutil.copy2(env_file, backup_path)
        return backup_path

    def migrate_service(self, service: str, dry_run: bool = False, force: bool = False) -> bool:
        """
        Run pending migrations for a service.
        Returns True if successful, False if errors occurred.
        """
        if service not in SERVICE_MIGRATIONS:
            print(f"No migrations defined for service: {service}")
            return True

        migrations = SERVICE_MIGRATIONS[service]
        current_version = self.get_applied_version(service) if not force else 0
        pending = [m for m in migrations if m["version"] > current_version]

        if not pending:
            print(f"{service}: Already at latest version (v{current_version})")
            return True

        env_file = self.get_env_file(service)

        print(f"\n{'='*60}")
        print(f"Service: {service}")
        print(f"Current version: {current_version}")
        print(f"Pending migrations: {len(pending)}")
        print(f"{'='*60}")

        for migration in pending:
            version = migration["version"]
            desc = migration["description"]

            print(f"\n[v{version}] {desc}")

            if migration.get("notes"):
                print("\nNotes:")
                for note in migration["notes"]:
                    print(f"  {note}")

            if not env_file.exists():
                print(f"\n  No env file found at {env_file}")
                print("  Creating placeholder for manual configuration...")

                if not dry_run:
                    env_file.parent.mkdir(parents=True, exist_ok=True)
                    with open(env_file, "w") as f:
                        f.write(f"# {service.upper()} Configuration\n")
                        f.write(f"# Migrated to new image format (v{version})\n")
                        f.write(f"# {migration.get('image_change', desc)}\n")
                        f.write("#\n")
                        if migration.get("notes"):
                            for note in migration["notes"]:
                                f.write(f"# {note}\n")
                        f.write("\n")
                    self.set_applied_version(service, version)
                continue

            # Parse existing env file
            lines = self.parse_env_file(env_file)

            # Apply transforms
            transforms = migration.get("transforms", {})
            modified = False

            if transforms:
                new_lines = []
                for line_type, var_name, content in lines:
                    if line_type == "var" and var_name in transforms:
                        new_var = transforms[var_name]
                        print(f"  Transform: {var_name} -> {new_var}")
                        # Comment out old var
                        new_lines.append(("comment", None, f"# MIGRATED: {var_name}={content}"))
                        # Add new var
                        new_lines.append(("var", new_var, content))
                        modified = True
                    else:
                        new_lines.append((line_type, var_name, content))
                lines = new_lines

            if dry_run:
                print("\n  [DRY RUN] Would apply migration")
                if modified:
                    print("  Changes would be written to env file")
            else:
                # Backup before modifying
                backup = self.backup_env_file(service)
                if backup:
                    print(f"\n  Backup: {backup.name}")

                # Add migration header if not already present
                header_lines = [
                    ("comment", None, f"# Migration v{version} applied: {datetime.now().isoformat()}"),
                    ("comment", None, f"# {migration.get('image_change', desc)}"),
                ]

                # Find insertion point (after existing headers)
                insert_idx = 0
                for i, (lt, _, _) in enumerate(lines):
                    if lt in ("comment", "empty"):
                        insert_idx = i + 1
                    else:
                        break

                lines = lines[:insert_idx] + header_lines + [("empty", None, "")] + lines[insert_idx:]

                self.write_env_file(env_file, lines)
                self.set_applied_version(service, version)
                print(f"\n  Applied migration v{version}")

        return True

    def migrate_all(self, dry_run: bool = False, force: bool = False) -> bool:
        """Run migrations for all services with pending changes."""
        success = True
        for service in SERVICE_MIGRATIONS:
            if not self.migrate_service(service, dry_run, force):
                success = False
        return success

    def list_migrations(self) -> None:
        """List all available migrations and their status."""
        state = self.load_state()
        applied = state.get("applied", {})

        print("\nService Environment Migrations")
        print("=" * 60)

        for service, migrations in sorted(SERVICE_MIGRATIONS.items()):
            current = applied.get(service, 0)
            latest = max(m["version"] for m in migrations)
            status = "up-to-date" if current >= latest else f"pending ({latest - current} migration(s))"

            print(f"\n{service}:")
            print(f"  Current: v{current}, Latest: v{latest} [{status}]")

            for m in migrations:
                marker = "[x]" if m["version"] <= current else "[ ]"
                print(f"  {marker} v{m['version']}: {m['description']}")

    def check_service(self, service: str) -> dict:
        """Check migration status for a service."""
        if service not in SERVICE_MIGRATIONS:
            return {"service": service, "defined": False}

        migrations = SERVICE_MIGRATIONS[service]
        current = self.get_applied_version(service)
        latest = max(m["version"] for m in migrations)

        return {
            "service": service,
            "defined": True,
            "current_version": current,
            "latest_version": latest,
            "up_to_date": current >= latest,
            "pending_count": sum(1 for m in migrations if m["version"] > current),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Migrate service environment variables for breaking image changes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  migrate_service_env.py list                    List all migrations and status
  migrate_service_env.py migrate samba           Migrate samba env vars
  migrate_service_env.py migrate --all           Migrate all services
  migrate_service_env.py migrate samba --dry-run Preview changes
  migrate_service_env.py check samba             Check migration status
        """,
    )

    parser.add_argument(
        "--base-dir",
        default="/app",
        help="Base directory (default: /app)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # list command
    list_parser = subparsers.add_parser("list", help="List all migrations")

    # migrate command
    migrate_parser = subparsers.add_parser("migrate", help="Run migrations")
    migrate_parser.add_argument("service", nargs="?", help="Service to migrate")
    migrate_parser.add_argument("--all", action="store_true", help="Migrate all services")
    migrate_parser.add_argument("--dry-run", action="store_true", help="Preview without changes")
    migrate_parser.add_argument("--force", action="store_true", help="Re-run even if already applied")

    # check command
    check_parser = subparsers.add_parser("check", help="Check migration status")
    check_parser.add_argument("service", help="Service to check")

    args = parser.parse_args()
    migrator = ServiceEnvMigrator(args.base_dir)

    if args.command == "list":
        migrator.list_migrations()
        return 0

    elif args.command == "migrate":
        if args.all:
            success = migrator.migrate_all(args.dry_run, args.force)
        elif args.service:
            success = migrator.migrate_service(args.service, args.dry_run, args.force)
        else:
            parser.error("Specify a service or use --all")
            return 1
        return 0 if success else 1

    elif args.command == "check":
        status = migrator.check_service(args.service)
        if not status["defined"]:
            print(f"No migrations defined for: {args.service}")
            return 0
        print(f"Service: {status['service']}")
        print(f"Current version: {status['current_version']}")
        print(f"Latest version: {status['latest_version']}")
        print(f"Status: {'up-to-date' if status['up_to_date'] else f'{status[\"pending_count\"]} pending'}")
        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
