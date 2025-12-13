#!/usr/bin/env python
"""
migrate_mariadb.py - Migrate services to shared MariaDB

This script automates migration of services from dedicated MariaDB/MySQL containers
to a shared MariaDB instance, similar to postgres migration pattern.

Usage:
    ./migrate_mariadb.py <service-name> [--dry-run] [--skip-backup]

Features:
- Detects dedicated MariaDB/MySQL containers in service YAMLs
- Creates timestamped backups before migration
- Automatically assigns unique database names
- Updates connection strings in service YAMLs
- Removes dedicated database containers
- Creates rollback override files
- Verifies migration success

Example:
    ./migrate_mariadb.py wallabag
    ./migrate_mariadb.py firefly3 --dry-run
"""

import argparse
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
import yaml


class MariaDBMigrator:
    """Manages migration of services to shared MariaDB."""

    def __init__(self, service_name: str, base_dir: str = "/apps/onramp"):
        self.service_name = service_name
        self.base_dir = Path(base_dir)
        self.service_file = self.base_dir / "services-available" / f"{service_name}.yml"
        self.manager_script = self.base_dir / "sietch" / "scripts" / "mariadb_manager.py"

    def parse_service_config(self) -> dict:
        """Parse service YAML to detect MariaDB containers and connection patterns."""
        if not self.service_file.exists():
            print(f"Error: Service file not found: {self.service_file}", file=sys.stderr)
            sys.exit(1)

        with open(self.service_file, 'r') as f:
            content = f.read()

        # Detect dedicated MariaDB/MySQL containers
        mariadb_containers = []
        
        # Look for mariadb/mysql images
        mariadb_pattern = r'^\s+(\w+(?:[\w-]+\w)?):\s*$.*?image:\s*(mariadb|mysql|lscr\.io/linuxserver/mariadb)'
        for match in re.finditer(mariadb_pattern, content, re.MULTILINE | re.DOTALL):
            container_name = match.group(1)
            if container_name != self.service_name:  # Not the main service
                mariadb_containers.append(container_name)

        # Detect connection patterns
        connection_patterns = {
            'MYSQL_HOST': re.search(r'MYSQL_HOST[=:](\S+)', content),
            'MARIADB_HOST': re.search(r'MARIADB_HOST[=:](\S+)', content),
            'DB_HOST': re.search(r'DB_HOST[=:](\S+)', content),
            'DATABASE_HOST': re.search(r'DATABASE_HOST[=:](\S+)', content),
            'SYMFONY__ENV__DATABASE_HOST': re.search(r'SYMFONY__ENV__DATABASE_HOST[=:](\S+)', content),
        }

        # Database name patterns
        db_name_patterns = {
            'MYSQL_DATABASE': re.search(r'MYSQL_DATABASE[=:](\S+)', content),
            'MARIADB_DATABASE': re.search(r'MARIADB_DATABASE[=:](\S+)', content),
            'DB_NAME': re.search(r'DB_NAME[=:](\S+)', content),
            'DATABASE_NAME': re.search(r'DATABASE_NAME[=:](\S+)', content),
            'SYMFONY__ENV__DATABASE_NAME': re.search(r'SYMFONY__ENV__DATABASE_NAME[=:](\S+)', content),
        }

        return {
            'mariadb_containers': mariadb_containers,
            'connection_patterns': {k: v.group(1) if v else None for k, v in connection_patterns.items()},
            'db_name_patterns': {k: v.group(1) if v else None for k, v in db_name_patterns.items()},
            'yaml_content': content,
        }

    def create_backup(self, container_name: str, db_name: str) -> Path:
        """Create database backup before migration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.base_dir / "backups" / "mariadb-migrations"
        backup_dir.mkdir(parents=True, exist_ok=True)
        backup_file = backup_dir / f"{self.service_name}_{db_name}_{timestamp}.sql"

        print(f"Creating backup of {db_name} from {container_name}...")
        
        cmd = [
            "docker", "exec", container_name,
            "mysqldump", "-u", "root", "-p${MYSQL_ROOT_PASSWORD}",
            "--single-transaction", "--routines", "--triggers",
            db_name
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                print(f"Warning: Backup failed: {result.stderr}", file=sys.stderr)
                return None

            backup_file.write_text(result.stdout)
            print(f"✓ Backup created: {backup_file}")
            return backup_file

        except subprocess.TimeoutExpired:
            print("Error: Backup timed out after 5 minutes", file=sys.stderr)
            return None
        except Exception as e:
            print(f"Error creating backup: {e}", file=sys.stderr)
            return None

    def create_database(self, db_name: str) -> bool:
        """Create database in shared MariaDB using manager."""
        print(f"Creating database '{db_name}' in shared MariaDB...")
        
        try:
            result = subprocess.run(
                [str(self.manager_script), "create-db", db_name],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                print(f"Error creating database: {result.stderr}", file=sys.stderr)
                return False

            print(f"✓ Database '{db_name}' created")
            return True

        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            return False

    def update_yaml(self, config: dict, db_name: str) -> bool:
        """Update service YAML to use shared MariaDB."""
        content = config['yaml_content']

        # Add metadata if not present
        if '# database: mariadb' not in content:
            # Find the description line and add metadata
            desc_pattern = r'(# description:.*?\n(?:# .*?\n)*)'
            metadata = f"# database: mariadb\n# database_name: {db_name}\n"
            
            if re.search(desc_pattern, content):
                content = re.sub(desc_pattern, f"\\1{metadata}", content, count=1)
            else:
                # Add at the beginning if no description
                content = f"# database: mariadb\n# database_name: {db_name}\n\n{content}"

        # Update connection strings
        replacements = []

        # Update host references
        for pattern_name, host_value in config['connection_patterns'].items():
            if host_value and host_value in config['mariadb_containers']:
                replacements.append((
                    f"{pattern_name}={host_value}",
                    f"{pattern_name}=mariadb"
                ))
                replacements.append((
                    f"{pattern_name}: {host_value}",
                    f"{pattern_name}: mariadb"
                ))

        # Update depends_on
        for container in config['mariadb_containers']:
            replacements.append((
                f"- {container}",
                "- mariadb"
            ))

        # Apply replacements
        for old, new in replacements:
            content = content.replace(old, new)

        # Remove dedicated MariaDB containers
        for container in config['mariadb_containers']:
            # Remove entire service definition
            service_pattern = rf'^  {re.escape(container)}:.*?(?=^  \w+:|\Z)'
            content = re.sub(service_pattern, '', content, flags=re.MULTILINE | re.DOTALL)

        # Write updated YAML
        try:
            with open(self.service_file, 'w') as f:
                f.write(content)
            print(f"✓ Updated {self.service_file}")
            return True
        except Exception as e:
            print(f"Error updating YAML: {e}", file=sys.stderr)
            return False

    def create_rollback_override(self, config: dict) -> bool:
        """Create override file to restore dedicated MariaDB."""
        override_file = self.base_dir / "overrides-available" / f"{self.service_name}-dedicated-mariadb.yml"

        # Extract original MariaDB service definition
        original_content = config['yaml_content']
        
        # Build rollback override
        rollback = f"""# Rollback override for {self.service_name}
# This restores the dedicated MariaDB/MySQL container
# Usage: make enable-override {self.service_name}-dedicated-mariadb

networks:
  database:

services:
"""

        # Add main service depends_on restoration
        main_depends = []
        for container in config['mariadb_containers']:
            main_depends.append(f"      - {container}")

        if main_depends:
            rollback += f"  {self.service_name}:\n    depends_on:\n"
            rollback += "\n".join(main_depends) + "\n\n"

        # Extract and add MariaDB container definitions
        for container in config['mariadb_containers']:
            service_pattern = rf'^  {re.escape(container)}:.*?(?=^  \w+:|\Z)'
            match = re.search(service_pattern, original_content, re.MULTILINE | re.DOTALL)
            if match:
                service_def = match.group(0)
                rollback += service_def + "\n"

        try:
            override_file.write_text(rollback)
            print(f"✓ Created rollback override: {override_file}")
            return True
        except Exception as e:
            print(f"Error creating rollback: {e}", file=sys.stderr)
            return False

    def verify_migration(self, db_name: str) -> bool:
        """Verify migration was successful."""
        print("Verifying migration...")
        
        # Check if database exists in shared MariaDB
        try:
            result = subprocess.run(
                [str(self.manager_script), "database-exists", db_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"✗ Database '{db_name}' not found in shared MariaDB", file=sys.stderr)
                return False

        except Exception as e:
            print(f"Error verifying database: {e}", file=sys.stderr)
            return False

        # Check YAML metadata
        with open(self.service_file, 'r') as f:
            content = f.read()
            if '# database: mariadb' not in content:
                print("✗ Missing mariadb metadata in YAML", file=sys.stderr)
                return False
            if f'# database_name: {db_name}' not in content:
                print(f"✗ Missing database_name metadata in YAML", file=sys.stderr)
                return False

        # Check connection strings updated
        config = self.parse_service_config()
        if config['mariadb_containers']:
            print("✗ Dedicated MariaDB containers still present", file=sys.stderr)
            return False

        print("✓ Migration verified successfully")
        return True

    def migrate(self, dry_run: bool = False, skip_backup: bool = False) -> int:
        """Run full migration process."""
        print(f"=== Migrating {self.service_name} to shared MariaDB ===\n")

        # Parse service configuration
        config = self.parse_service_config()
        
        if not config['mariadb_containers']:
            print(f"No dedicated MariaDB/MySQL containers found in {self.service_name}")
            print("This service may already be using shared MariaDB or doesn't use MariaDB.")
            return 1

        print(f"Found dedicated containers: {', '.join(config['mariadb_containers'])}")

        # Determine database name
        db_name = None
        for pattern, value in config['db_name_patterns'].items():
            if value:
                db_name = value.replace('${', '').replace('}', '').replace(':-', '_')
                break
        
        if not db_name:
            db_name = self.service_name

        print(f"Target database name: {db_name}")

        if dry_run:
            print("\n[DRY RUN] Would perform:")
            print(f"  1. Backup from containers: {config['mariadb_containers']}")
            print(f"  2. Create database: {db_name}")
            print(f"  3. Update YAML connection strings")
            print(f"  4. Remove dedicated containers")
            print(f"  5. Create rollback override")
            return 0

        # Backup databases
        if not skip_backup:
            for container in config['mariadb_containers']:
                backup = self.create_backup(container, db_name)
                if not backup:
                    print("Warning: Continuing without backup")

        # Create database in shared MariaDB
        if not self.create_database(db_name):
            print("Migration failed: Could not create database", file=sys.stderr)
            return 1

        # Update YAML
        if not self.update_yaml(config, db_name):
            print("Migration failed: Could not update YAML", file=sys.stderr)
            return 1

        # Create rollback override
        if not self.create_rollback_override(config):
            print("Warning: Could not create rollback override")

        # Verify migration
        if not self.verify_migration(db_name):
            print("Migration completed with warnings", file=sys.stderr)
            return 1

        print(f"\n✓ Migration complete!")
        print(f"  Database: {db_name}")
        print(f"  Connection: mariadb:3306")
        print(f"\nNext steps:")
        print(f"  1. Review changes in {self.service_file}")
        print(f"  2. Test with: make up {self.service_name}")
        print(f"  3. Rollback if needed: make enable-override {self.service_name}-dedicated-mariadb")

        return 0


def main():
    parser = argparse.ArgumentParser(description="Migrate service to shared MariaDB")
    parser.add_argument("service", help="Service name to migrate")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without doing it")
    parser.add_argument("--skip-backup", action="store_true", help="Skip database backup step")
    
    args = parser.parse_args()

    migrator = MariaDBMigrator(args.service)
    return migrator.migrate(dry_run=args.dry_run, skip_backup=args.skip_backup)


if __name__ == "__main__":
    sys.exit(main())
