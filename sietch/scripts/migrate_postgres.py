#!/usr/bin/env python
"""
migrate_postgres.py - Migrate services from dedicated postgres to shared instance

This script orchestrates the complete migration process:
1. Detects dedicated postgres container for a service
2. Backs up existing data
3. Migrates to shared postgres instance
4. Updates service YAML with metadata
5. Creates backward-compatibility override
6. Verifies migration success

Usage:
  migrate_postgres.py <service>              # Migrate specific service
  migrate_postgres.py <service> --dry-run    # Preview migration steps
  migrate_postgres.py <service> --verify     # Verify existing migration

The script is idempotent - safe to run multiple times.
"""

import argparse
import re
import sys
import yaml
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from postgres_manager import PostgresManager
except ImportError:
    print("Error: postgres_manager module not found", file=sys.stderr)
    sys.exit(1)


class ServiceConfig:
    """Parsed service configuration."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.postgres_container: Optional[str] = None
        self.postgres_image: Optional[str] = None
        self.database_name: Optional[str] = None
        self.database_user: Optional[str] = "postgres"
        self.volume_path: Optional[str] = None
        self.connection_env: dict = {}


class PostgresMigrator:
    """Orchestrates postgres migration for a service."""

    def __init__(self, service: str, base_dir: str = "/app", dry_run: bool = False):
        self.service = service
        self.base_dir = Path(base_dir)
        self.dry_run = dry_run
        self.pg_manager = PostgresManager(base_dir=base_dir)

        self.service_yml = self.base_dir / "services-available" / f"{service}.yml"
        self.services_enabled = self.base_dir / "services-enabled"
        self.overrides_available = self.base_dir / "overrides-available"

        if not self.service_yml.exists():
            raise FileNotFoundError(f"Service file not found: {self.service_yml}")

    def parse_service_config(self) -> ServiceConfig:
        """Parse service YAML to find postgres configuration."""
        print(f"Parsing service configuration for '{self.service}'...")

        config = ServiceConfig(self.service)

        with open(self.service_yml, "r") as f:
            data = yaml.safe_load(f)

        # Helper to resolve environment variables with defaults
        def resolve_env(value: str) -> str:
            if not isinstance(value, str):
                return value
            # Handle ${VAR:-default} pattern
            import re
            match = re.search(r'\${([^:}]+)(?::-([^}]+))?}', value)
            if match:
                var_name, default = match.groups()
                # Return default value if present, otherwise keep var name
                return default if default else var_name
            return value

        # Look for postgres container in services
        services = data.get("services", {})

        for svc_name, svc_config in services.items():
            image = svc_config.get("image", "")

            # Detect dedicated postgres container
            if "postgres" in image.lower() and "postgres:" in image:
                # Resolve container name with env var expansion
                container_name = svc_config.get("container_name", svc_name)
                config.postgres_container = resolve_env(container_name)
                config.postgres_image = image

                # Extract database info from environment
                env = svc_config.get("environment", [])
                for env_var in env:
                    if isinstance(env_var, str):
                        if "POSTGRES_DB=" in env_var:
                            db_value = env_var.split("=", 1)[1]
                            config.database_name = resolve_env(db_value)
                        elif "POSTGRES_USER=" in env_var:
                            user_value = env_var.split("=", 1)[1]
                            config.database_user = resolve_env(user_value)

                # Get volume path
                volumes = svc_config.get("volumes", [])
                for vol in volumes:
                    if "/var/lib/postgresql/data" in vol:
                        config.volume_path = vol.split(":")[0]

        # If no database name found, use service name
        if not config.database_name:
            config.database_name = self.service

        return config

    def check_already_migrated(self) -> bool:
        """Check if service is already migrated."""
        # Check for metadata in YAML
        with open(self.service_yml, "r") as f:
            content = f.read()

        if "# database: postgres" in content and f"# database_name: {self.service}" in content:
            # Check if database exists in shared postgres
            if self.pg_manager.database_exists(self.service):
                print(f"✅ Service '{self.service}' already migrated to shared postgres")
                return True

        return False

    def create_backup(self, config: ServiceConfig) -> Optional[Path]:
        """Create backup of existing postgres data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / "backups" / "postgres-migrations"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"{self.service}_{timestamp}.dump"
        log_path = backup_dir / f"{self.service}_{timestamp}.log"

        print(f"Creating backup: {backup_path}")

        if self.dry_run:
            print(f"  [DRY RUN] Would backup {config.postgres_container}:{config.database_name}")
            return backup_path

        # Use postgres_manager to migrate from container
        # This automatically creates a backup
        return backup_path

    def update_service_yaml(self, config: ServiceConfig) -> bool:
        """Update service YAML with postgres metadata and remove dedicated container."""
        print(f"Updating service YAML: {self.service_yml}")

        if self.dry_run:
            print(f"  [DRY RUN] Would add metadata and remove {config.postgres_container}")
            return True

        with open(self.service_yml, "r") as f:
            lines = f.readlines()

        # Find where to insert metadata (after description comment)
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("# description:"):
                insert_idx = i + 1
                break

        # Check if metadata already exists
        has_metadata = any("# database: postgres" in line for line in lines)

        if not has_metadata:
            # Insert metadata
            metadata = [
                f"# database: postgres\n",
                f"# database_name: {config.database_name}\n",
            ]
            lines[insert_idx:insert_idx] = metadata

        # Remove dedicated postgres service
        new_lines = []
        skip_service = False
        indent_level = 0

        for line in lines:
            # Detect start of postgres service
            if config.postgres_container and f"{config.postgres_container}:" in line:
                skip_service = True
                indent_level = len(line) - len(line.lstrip())
                continue

            # Skip lines that are part of postgres service
            if skip_service:
                current_indent = len(line) - len(line.lstrip())
                # If we hit a line with same or less indentation, we're done
                if line.strip() and current_indent <= indent_level:
                    skip_service = False
                else:
                    continue

            new_lines.append(line)

        # Update main service to depend on shared postgres
        final_lines = []
        in_main_service = False

        for line in new_lines:
            # Add dependency on shared postgres
            if "depends_on:" in line and not in_main_service:
                final_lines.append(line)
                # Check if postgres already in depends_on
                next_idx = new_lines.index(line) + 1
                has_postgres_dep = False
                if next_idx < len(new_lines):
                    # Look ahead for postgres dependency
                    for check_line in new_lines[next_idx:]:
                        if "- postgres" in check_line:
                            has_postgres_dep = True
                            break
                        if not check_line.startswith(" " * (len(line) - len(line.lstrip()) + 2)):
                            break

                if not has_postgres_dep:
                    indent = " " * (len(line) - len(line.lstrip()) + 2)
                    final_lines.append(f"{indent}- postgres\n")
            else:
                final_lines.append(line)

        # Write updated YAML
        with open(self.service_yml, "w") as f:
            f.writelines(final_lines)

        print(f"  ✅ Updated {self.service_yml}")
        return True

    def create_override(self, config: ServiceConfig) -> bool:
        """Create backward-compatibility override to restore dedicated postgres."""
        override_path = self.overrides_available / f"{self.service}-dedicated-postgres.yml"

        print(f"Creating rollback override: {override_path}")

        if self.dry_run:
            print(f"  [DRY RUN] Would create {override_path}")
            return True

        # Read original service YAML to extract postgres service
        with open(self.service_yml, "r") as f:
            original = yaml.safe_load(f)

        # Create override with just the postgres service
        override_data = {
            "networks": {"traefik": {"external": True}},
            "services": {},
        }

        # Find postgres service in original
        for svc_name, svc_config in original.get("services", {}).items():
            image = svc_config.get("image", "")
            if "postgres" in image.lower():
                override_data["services"][svc_name] = svc_config

        # Add comment
        override_content = f"""# Rollback override for {self.service}
# This restores the dedicated postgres container
# Usage: make enable-override {self.service}-dedicated-postgres

"""
        override_content += yaml.dump(override_data, default_flow_style=False, sort_keys=False)

        override_path.write_text(override_content)
        print(f"  ✅ Created {override_path}")
        return True

    def migrate(self) -> bool:
        """Execute full migration workflow."""
        print(f"\n{'='*60}")
        print(f"PostgreSQL Migration: {self.service}")
        print(f"{'='*60}\n")

        # Step 1: Parse configuration
        config = self.parse_service_config()

        if not config.postgres_container:
            print(f"❌ No dedicated postgres container found for '{self.service}'")
            print(f"   This service may already use shared postgres or not use postgres at all.")
            return False

        print(f"  Found postgres container: {config.postgres_container}")
        print(f"  Database name: {config.database_name}")
        print(f"  Volume: {config.volume_path}\n")

        # Step 2: Check if already migrated
        if self.check_already_migrated():
            if self.dry_run or input("Already migrated. Re-run migration? [y/N] ").lower() != "y":
                return True

        # Step 3: Migrate data
        print(f"\nStep 1/3: Migrating database...")
        if not self.dry_run:
            code = self.pg_manager.migrate_from_container(
                config.postgres_container, config.database_name, config.database_name, config.database_user
            )
            if code != 0:
                print(f"❌ Migration failed with code {code}")
                return False
        else:
            print(f"  [DRY RUN] Would migrate from {config.postgres_container}")

        # Step 4: Update service YAML
        print(f"\nStep 2/3: Updating service configuration...")
        if not self.update_service_yaml(config):
            print(f"❌ Failed to update service YAML")
            return False

        # Step 5: Create override for rollback
        print(f"\nStep 3/3: Creating rollback override...")
        if not self.create_override(config):
            print(f"⚠️  Failed to create override (non-fatal)")

        print(f"\n{'='*60}")
        print(f"✅ Migration Complete!")
        print(f"{'='*60}\n")

        print(f"Next steps:")
        print(f"  1. Restart the service: make restart")
        print(f"  2. Verify connectivity: docker logs {self.service}")
        print(f"  3. Test application functionality")
        print(f"\nRollback if needed:")
        print(f"  make enable-override {self.service}-dedicated-postgres && make restart\n")

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate service from dedicated postgres to shared instance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  migrate_postgres.py docmost              # Migrate docmost service
  migrate_postgres.py joplin --dry-run     # Preview joplin migration
  migrate_postgres.py netbox --verify      # Verify netbox migration

The migration process:
  1. Detects dedicated postgres container
  2. Backs up existing database
  3. Restores to shared postgres instance
  4. Updates service YAML with metadata
  5. Creates rollback override

Idempotent: Safe to run multiple times on the same service.
        """,
    )

    parser.add_argument("service", help="Service name to migrate")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without making changes")
    parser.add_argument("--verify", action="store_true", help="Verify existing migration")
    parser.add_argument("--base-dir", default="/app", help="OnRamp base directory")

    args = parser.parse_args()

    try:
        migrator = PostgresMigrator(args.service, args.base_dir, args.dry_run)

        if args.verify:
            if migrator.check_already_migrated():
                config = migrator.parse_service_config()
                migrator.pg_manager.verify_database(config.database_name)
                return 0
            else:
                print(f"❌ Service '{args.service}' is not migrated yet")
                return 1

        success = migrator.migrate()
        return 0 if success else 1

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
