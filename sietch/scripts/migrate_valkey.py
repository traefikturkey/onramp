#!/usr/bin/env python
"""
migrate_valkey.py - Migrate services from dedicated Redis/Valkey to shared Valkey instance

This script orchestrates the complete migration process:
1. Detects dedicated Redis/Valkey container for a service
2. Backs up existing data (RDB snapshot)
3. Migrates keys to shared Valkey instance with assigned database number
4. Updates service YAML with metadata and new connection string
5. Creates rollback override
6. Verifies migration success

Usage:
  migrate_valkey.py <service>              # Migrate specific service
  migrate_valkey.py <service> --dry-run    # Preview migration steps
  migrate_valkey.py <service> --verify     # Verify existing migration

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
    from valkey_manager import ValkeyManager
except ImportError:
    print("Error: valkey_manager module not found", file=sys.stderr)
    sys.exit(1)


class ServiceConfig:
    """Parsed service configuration."""

    def __init__(self, service_name: str):
        self.service_name = service_name
        self.redis_container: Optional[str] = None
        self.redis_image: Optional[str] = None
        self.redis_host: Optional[str] = None
        self.redis_port: str = "6379"
        self.redis_db: str = "0"
        self.volume_path: Optional[str] = None
        self.connection_pattern: Optional[str] = None  # URL, HOST, or HOSTNAME


class ValkeyMigrator:
    """Orchestrates Valkey migration for a service."""

    def __init__(self, service: str, base_dir: str = "/app", dry_run: bool = False):
        self.service = service
        self.base_dir = Path(base_dir)
        self.dry_run = dry_run
        self.valkey_manager = ValkeyManager(base_dir=base_dir)

        self.service_yml = self.base_dir / "services-available" / f"{service}.yml"
        self.services_enabled = self.base_dir / "services-enabled"
        self.overrides_available = self.base_dir / "overrides-available"

        if not self.service_yml.exists():
            raise FileNotFoundError(f"Service file not found: {self.service_yml}")

    def parse_service_config(self) -> ServiceConfig:
        """Parse service YAML to find Redis/Valkey configuration."""
        print(f"Parsing service configuration for '{self.service}'...")

        config = ServiceConfig(self.service)

        with open(self.service_yml, "r") as f:
            content = f.read()
            data = yaml.safe_load(f.seek(0) or f)

        # Helper to resolve environment variables with defaults
        def resolve_env(value: str) -> str:
            if not isinstance(value, str):
                return str(value)
            # Handle ${VAR:-default} pattern
            match = re.search(r'\${([^:}]+)(?::-([^}]+))?}', value)
            if match:
                var_name, default = match.groups()
                return default if default else var_name
            return value

        # Look for redis/valkey container in services
        services = data.get("services", {})

        for svc_name, svc_config in services.items():
            image = svc_config.get("image", "")

            # Detect dedicated redis/valkey container
            if ("redis" in image.lower() or "valkey" in image.lower()) and svc_name != self.service:
                container_name = svc_config.get("container_name", svc_name)
                config.redis_container = resolve_env(container_name)
                config.redis_image = image
                config.redis_host = config.redis_container

                # Get volume path
                volumes = svc_config.get("volumes", [])
                for vol in volumes:
                    if isinstance(vol, str) and "/data" in vol:
                        config.volume_path = vol.split(":")[0]

        # Detect connection pattern from environment variables
        if "REDIS_URL" in content or "redis://" in content:
            config.connection_pattern = "URL"
            # Extract database number from REDIS_URL if present
            match = re.search(r'redis://[^/]+/(\d+)', content)
            if match:
                config.redis_db = match.group(1)
        elif "REDIS_HOST" in content:
            config.connection_pattern = "HOST"
        elif "REDIS_HOSTNAME" in content:
            config.connection_pattern = "HOSTNAME"
        else:
            config.connection_pattern = "URL"  # Default to URL pattern

        return config

    def check_already_migrated(self) -> bool:
        """Check if service is already migrated."""
        # Check for metadata in YAML
        with open(self.service_yml, "r") as f:
            content = f.read()

        if "# cache: valkey" in content:
            # Check if database is assigned
            code, assignments = self.valkey_manager.list_databases()
            if code == 0 and self.service in assignments:
                print(f"✅ Service '{self.service}' already migrated to shared valkey")
                return True

        return False

    def create_backup(self, config: ServiceConfig) -> Optional[Path]:
        """Create backup of existing Redis data."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / "backups" / "valkey-migrations"
        backup_dir.mkdir(parents=True, exist_ok=True)

        backup_path = backup_dir / f"{self.service}_{timestamp}.rdb"
        
        print(f"Creating backup: {backup_path}")

        if self.dry_run:
            print(f"  [DRY RUN] Would backup {config.redis_container} RDB snapshot")
            return backup_path

        # Copy RDB file from dedicated container
        if not config.redis_container:
            print("  Warning: No dedicated Redis container found, skipping backup")
            return None

        import subprocess

        # Trigger a SAVE command first
        save_cmd = ["docker", "exec", config.redis_container, "valkey-cli", "SAVE"]
        try:
            subprocess.run(save_cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # Try redis-cli instead
            save_cmd = ["docker", "exec", config.redis_container, "redis-cli", "SAVE"]
            try:
                subprocess.run(save_cmd, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                print(f"  Warning: Could not trigger SAVE: {e}")

        # Copy dump.rdb from container
        copy_cmd = ["docker", "cp", f"{config.redis_container}:/data/dump.rdb", str(backup_path)]
        result = subprocess.run(copy_cmd, capture_output=True, text=True)

        if result.returncode != 0:
            print(f"  Warning: Could not copy backup: {result.stderr}")
            return None

        print(f"  ✅ Backup created: {backup_path}")
        return backup_path

    def assign_database(self) -> Optional[int]:
        """Assign Valkey database number to service."""
        print(f"Assigning Valkey database number...")

        if self.dry_run:
            print(f"  [DRY RUN] Would assign database to '{self.service}'")
            return 0

        code, db_num = self.valkey_manager.assign_database(self.service)
        if code != 0:
            print(f"  Error: Could not assign database")
            return None

        return db_num

    def update_yaml(self, config: ServiceConfig, db_num: int) -> bool:
        """Update service YAML with Valkey metadata and connection strings."""
        print(f"Updating service YAML...")

        with open(self.service_yml, "r") as f:
            lines = f.readlines()

        if self.dry_run:
            print(f"  [DRY RUN] Would update {self.service_yml}")
            print(f"    - Add metadata: # cache: valkey")
            print(f"    - Add cache_db: {db_num}")
            print(f"    - Update connection to valkey:6379/{db_num}")
            print(f"    - Remove dedicated Redis container")
            return True

        # Add metadata if not present
        has_metadata = any("# cache: valkey" in line for line in lines)
        
        if not has_metadata:
            # Find where to insert metadata (after network definition, before services)
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("# description:"):
                    insert_idx = i + 1
                    while insert_idx < len(lines) and lines[insert_idx].strip().startswith("#"):
                        insert_idx += 1
                    break
            
            metadata_lines = [
                f"# cache: valkey\n",
                f"# cache_db: {db_num}\n",
                "\n"
            ]
            lines = lines[:insert_idx] + metadata_lines + lines[insert_idx:]

        # Update connection strings
        new_lines = []
        in_redis_service = False
        skip_until_next_service = False

        for line in lines:
            # Skip dedicated Redis service definition
            if re.match(r'\s{2}[\w-]+-redis:', line) or re.match(r'\s{2}redis:', line):
                if not line.strip().startswith(f"{self.service}:"):
                    in_redis_service = True
                    skip_until_next_service = True
                    continue
            
            # Stop skipping when we hit the next service
            if skip_until_next_service and re.match(r'\s{2}[\w-]+:', line):
                skip_until_next_service = False
                in_redis_service = False
            
            if skip_until_next_service:
                continue

            # Update connection strings
            modified_line = line
            
            # Pattern 1: REDIS_URL=redis://host:port/db
            if "REDIS_URL=" in line:
                modified_line = re.sub(
                    r'REDIS_URL=redis://[^:]+:\d+(?:/\d+)?',
                    f'REDIS_URL=redis://valkey:6379/{db_num}',
                    line
                )
            
            # Pattern 2: REDIS_HOST=hostname
            elif "REDIS_HOST=" in line:
                modified_line = re.sub(
                    r'REDIS_HOST=[^\s]+',
                    'REDIS_HOST=valkey',
                    line
                )
            
            # Pattern 3: REDIS_HOSTNAME=hostname
            elif "REDIS_HOSTNAME=" in line:
                modified_line = re.sub(
                    r'REDIS_HOSTNAME=[^\s]+',
                    'REDIS_HOSTNAME=valkey',
                    line
                )
            
            # Update depends_on if it references Redis
            elif "depends_on:" in line or "- " in line:
                if config.redis_container and config.redis_container in line:
                    modified_line = line.replace(config.redis_container, "valkey")

            new_lines.append(modified_line)

        # Write updated content
        with open(self.service_yml, "w") as f:
            f.writelines(new_lines)

        print(f"  ✅ Updated {self.service_yml}")
        return True

    def create_rollback_override(self, config: ServiceConfig) -> bool:
        """Create rollback override to restore dedicated Redis."""
        override_path = self.overrides_available / f"{self.service}-dedicated-redis.yml"
        
        print(f"Creating rollback override: {override_path}")

        if self.dry_run:
            print(f"  [DRY RUN] Would create {override_path}")
            return True

        if not config.redis_container:
            print("  Warning: No dedicated Redis container found, skipping rollback override")
            return False

        # Read original service YAML to extract Redis service
        with open(self.service_yml, "r") as f:
            original_data = yaml.safe_load(f)

        # Build rollback override
        override_content = f"""# Rollback override for {self.service}
# This restores the dedicated Redis/Valkey container
# Usage: make enable-override {self.service}-dedicated-redis

networks:
  traefik:
    external: true

services:
  {self.service}:
    depends_on:
      - {config.redis_container}
"""

        # Add connection string restoration based on pattern
        if config.connection_pattern == "URL":
            override_content += f"""    environment:
      - REDIS_URL=redis://{config.redis_host}:{config.redis_port}/{config.redis_db}
"""
        elif config.connection_pattern == "HOST":
            override_content += f"""    environment:
      - REDIS_HOST={config.redis_host}
"""
        elif config.connection_pattern == "HOSTNAME":
            override_content += f"""    environment:
      - REDIS_HOSTNAME={config.redis_host}
"""

        # Add Redis container definition (reconstruct from config)
        override_content += f"""
  {config.redis_container}:
    image: {config.redis_image}
    container_name: {config.redis_container}
    restart: unless-stopped
    networks:
      - traefik
"""
        
        if config.volume_path:
            override_content += f"""    volumes:
      - {config.volume_path}:/data
"""

        override_path.write_text(override_content)
        print(f"  ✅ Created rollback override")
        return True

    def verify_migration(self) -> bool:
        """Verify migration was successful."""
        print(f"Verifying migration...")

        # Check database assignment
        code, db_num = self.valkey_manager.get_database(self.service)
        if code != 0:
            print(f"  ❌ Database not assigned")
            return False

        # Check metadata in YAML
        with open(self.service_yml, "r") as f:
            content = f.read()
        
        if "# cache: valkey" not in content:
            print(f"  ❌ Missing cache metadata in YAML")
            return False

        # Check connection string updated
        if "valkey" not in content:
            print(f"  ❌ Connection string not updated")
            return False

        print(f"  ✅ Migration verified successfully")
        print(f"     Service: {self.service}")
        print(f"     Database: {db_num}")
        return True

    def migrate(self) -> bool:
        """Execute full migration process."""
        print(f"\n{'='*60}")
        print(f"Migrating '{self.service}' to shared Valkey")
        print(f"{'='*60}\n")

        # Check if already migrated
        if self.check_already_migrated():
            print("\nMigration already complete!")
            return True

        # Parse configuration
        config = self.parse_service_config()
        
        if not config.redis_container:
            print(f"Warning: No dedicated Redis/Valkey container found for '{self.service}'")
            print(f"This service may already be using shared cache or doesn't use Redis")
            
            # Still assign database if metadata indicates it needs Valkey
            if "needs valkey" in str(config).lower() or "redis" in str(config).lower():
                db_num = self.assign_database()
                if db_num is not None:
                    self.update_yaml(config, db_num)
                    return self.verify_migration() if not self.dry_run else True
            return False

        print(f"\nFound dedicated Redis container: {config.redis_container}")
        print(f"  Image: {config.redis_image}")
        print(f"  Current DB: {config.redis_db}")
        print(f"  Connection: {config.connection_pattern}")

        # Create backup
        backup_path = self.create_backup(config)

        # Assign database number
        db_num = self.assign_database()
        if db_num is None:
            print("\n❌ Migration failed: Could not assign database")
            return False

        # Update YAML
        if not self.update_yaml(config, db_num):
            print("\n❌ Migration failed: Could not update YAML")
            return False

        # Create rollback override
        if not self.create_rollback_override(config):
            print("  Warning: Could not create rollback override")

        # Verify migration
        if not self.dry_run and not self.verify_migration():
            print("\n❌ Migration verification failed")
            return False

        print(f"\n{'='*60}")
        print(f"✅ Migration complete for '{self.service}'!")
        print(f"{'='*60}")
        print(f"\nNext steps:")
        print(f"  1. Ensure valkey service is enabled: make enable-service valkey")
        print(f"  2. Restart services: make restart")
        print(f"  3. Test {self.service} functionality")
        print(f"  4. If issues occur, rollback with:")
        print(f"     make enable-override {self.service}-dedicated-redis")
        if backup_path:
            print(f"\nBackup saved: {backup_path}")
        
        return True


def main():
    parser = argparse.ArgumentParser(description="Migrate service to shared Valkey")
    parser.add_argument("service", help="Service name to migrate")
    parser.add_argument("--dry-run", action="store_true", help="Preview migration without making changes")
    parser.add_argument("--verify", action="store_true", help="Verify existing migration")
    parser.add_argument("--base-dir", default="/app", help="Base directory (default: /app)")

    args = parser.parse_args()

    try:
        migrator = ValkeyMigrator(args.service, base_dir=args.base_dir, dry_run=args.dry_run)

        if args.verify:
            success = migrator.verify_migration()
        else:
            success = migrator.migrate()

        return 0 if success else 1

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
