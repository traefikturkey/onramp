#!/usr/bin/env python
"""
migrate-env.py - Environment migration for OnRamp

Supports two migration paths:
1. Legacy master branch: monolithic .env -> modular services-enabled/*.env
2. Feature branch (onramp-rework-env): environments-enabled/*.env -> services-enabled/*.env

Feature branch structure:
  environments-available/*.template  - Source templates (deleted after migration)
  environments-enabled/*.env         - Generated env files (migrated then deleted)

Detection logic:
  .env exists AND services-enabled/.env missing -> legacy migration
  environments-enabled/ exists AND services-enabled/.env missing -> feature branch migration
"""

import argparse
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path


# Global variables that should go to services-enabled/.env
GLOBAL_VARS = {
    # Core configuration
    "CF_API_EMAIL",
    "CF_DNS_API_TOKEN",
    "HOST_NAME",
    "HOST_DOMAIN",
    "TZ",
    "PUID",
    "PGID",
    # Traefik settings
    "DNS_CHALLENGE_API_EMAIL",
    "DNS_CHALLENGE_PROVIDER",
    "TRAEFIK_ACCESSLOG",
    "TRAEFIK_LOG_LEVEL",
    "TRAEFIK_DASHBOARD_ENABLE",
    # Azure DNS settings
    "AZURE_CLIENT_ID",
    "AZURE_CLIENT_SECRET",
    "AZURE_SUBSCRIPTION_ID",
    "AZURE_TENANT_ID",
    "AZURE_RESOURCE_GROUP",
    # Backup settings
    "ONRAMP_BACKUP_LOCATION_ENV",
    "ONRAMP_BACKUP_EXCLUSIONS",
    "ONRAMP_BACKUP_INCLUSIONS",
    # Plex network
    "PLEX_ALLOWED_NETWORKS",
}

# Service prefix to service name mapping
SERVICE_PREFIXES = {
    "ADGUARD": "adguard",
    "AIRPRINT": "airprint",
    "AUDIOBOOKSHELF": "audiobookshelf",
    "AUTHELIA": "authelia",
    "AUTH_DOMAIN": "authelia",  # Special case
    "AUTHENTIK": "authentik",
    "AUTOHEAL": "autoheal",
    "BASARAN": "basaran",
    "BAZARR": "bazarr",
    "CLOUDFLARE_DDNS": "cloudflare-ddns",
    "CLOUDFLARED": "cloudflare-tunnel",
    "CLOUDFLARE_TUNNEL": "cloudflare-tunnel",
    "CODE_SERVER": "code-server",
    "DRONECI": "droneci",
    "FACTORIO": "factorio",
    "FLAME": "flame",
    "FOUNDRYVTT": "foundryvtt",
    "GHOST": "ghost",
    "GITEA": "gitea",
    "GOTIFY": "gotify",
    "GRAFANA": "grafana",
    "HEALTHCHECKS": "healthchecks",
    "HOMER": "homer",
    "IMMICH": "immich",
    "INFLUXDB": "influxdb",
    "ITFLOW": "itflow",
    "JELLYFIN": "jellyfin",
    "JELLYSEERR": "jellyseerr",
    "JOPLIN": "joplin",
    "JOYRIDE": "joyride",
    "KANEO": "kaneo",
    "KOMGA": "komga",
    "LIBRESPEED": "librespeed",
    "LIDARR": "lidarr",
    "LOKI": "loki",
    "MAILHOG": "mailhog",
    "MAILRISE": "mailrise",
    "MAKEMKV": "makemkv",
    "MARIADB": "mariadb",
    "MEALIE": "mealie",
    "MINECRAFT": "minecraft",
    "MONOCKER": "monocker",
    "NEXTCLOUD": "nextcloud",
    "NGINX_PROXY_MANAGER": "nginx-proxy-manager",
    "NOCODB": "nocodb",
    "OBSIDIAN": "obsidian",
    "OLLAMA": "ollama",
    "OMADA": "omada",
    "ONBOARD": "onboard",
    "OVERSEERR": "overseerr",
    "PAPERLESS": "paperless",
    "PG_PASS": "postgres",  # Generic postgres
    "PHOTOPRISM": "photoprism",
    "PIHOLE": "pihole",
    "PINCHFLAT": "pinchflat",
    "PLEX": "plex",
    "PLEXPY": "tautulli",  # Alias
    "POCKETBASE": "pocketbase",
    "PORTAINER": "portainer",
    "POSTGRES": "postgres",
    "PROMETHEUS": "prometheus",
    "PROWLARR": "prowlarr",
    "RADARR": "radarr",
    "READARR": "readarr",
    "RECIPES": "recipes",
    "RECYCLARR": "recyclarr",
    "REDIS": "redis",
    "REGISTRY": "registry",
    "REQUESTRR": "requestrr",
    "RESTIC": "restic",
    "SABNZBD": "sabnzbd",
    "SCRUTINY": "scrutiny",
    "SEARXNG": "searxng",
    "SONARR": "sonarr",
    "TAUTULLI": "tautulli",
    "TRAEFIK": "traefik",
    "TRANSMISSION": "transmission",
    "TRILIUM": "trilium",
    "TUBESYNC": "tubesync",
    "UNIFI": "unifi",
    "UPTIME_KUMA": "uptime-kuma",
    "VAULTWARDEN": "vaultwarden",
    "WATCHTOWER": "watchtower",
    "WORDPRESS": "wordpress",
    "WYZE_BRIDGE": "wyze-bridge",
    "YOURLS": "yourls",
}

# Feature branch special file mappings
# environments-enabled/onramp-X.env -> services-enabled/.env.X
FEATURE_BRANCH_SPECIAL_FILES = {
    "onramp-external": ".env.external",
    "onramp-nfs": ".env.nfs",
}


class EnvMigrator:
    """Handles migration from legacy .env or feature branch to modular environment system."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.legacy_env = self.base_dir / ".env"
        self.environments_enabled = self.base_dir / "environments-enabled"
        self.environments_available = self.base_dir / "environments-available"
        self.services_enabled = self.base_dir / "services-enabled"
        self.backups_dir = self.base_dir / "backups"

    def should_migrate_legacy(self) -> bool:
        """Check if legacy .env migration should run."""
        return self.legacy_env.exists() and not (self.services_enabled / ".env").exists()

    def should_migrate_feature_branch(self) -> bool:
        """
        Check if feature branch migration should run.

        Feature branch indicators:
        - environments-available/*.template files (strong indicator)
        - environments-enabled/*.env files (generated configs)

        Either indicator is sufficient to trigger feature branch migration.
        """
        has_templates = (
            self.environments_available.exists()
            and any(self.environments_available.glob("*.template"))
        )
        has_env_files = (
            self.environments_enabled.exists()
            and any(self.environments_enabled.glob("*.env"))
        )
        return (has_templates or has_env_files) and not (self.services_enabled / ".env").exists()

    def should_migrate(self) -> bool:
        """Check if any migration should run (legacy compatibility)."""
        return self.should_migrate_legacy() or self.should_migrate_feature_branch()

    def parse_env_file(self, path: Path) -> dict[str, tuple[str, list[str]]]:
        """
        Parse an env file into a dict of var_name -> (value, preceding_comments).
        Preserves comments that precede each variable.
        """
        variables: dict[str, tuple[str, list[str]]] = {}
        current_comments: list[str] = []

        with open(path, "r") as f:
            for line in f:
                line = line.rstrip("\n\r")

                # Empty line or comment
                if not line or line.startswith("#"):
                    current_comments.append(line)
                    continue

                # Variable assignment
                match = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line)
                if match:
                    var_name, value = match.groups()
                    variables[var_name] = (value, current_comments.copy())
                    current_comments = []
                else:
                    # Keep non-matching lines as comments
                    current_comments.append(line)

        return variables

    def get_service_for_var(self, var_name: str) -> str | None:
        """Determine which service a variable belongs to."""
        if var_name in GLOBAL_VARS:
            return None

        # Check each prefix
        for prefix, service in SERVICE_PREFIXES.items():
            if var_name.startswith(prefix + "_") or var_name == prefix:
                return service

        # Check if enabled service matches
        for yml in self.services_enabled.glob("*.yml"):
            service = yml.stem.upper().replace("-", "_")
            if var_name.startswith(service + "_") or var_name == service:
                return yml.stem

        return None

    def write_env_file(
        self, path: Path, variables: dict[str, tuple[str, list[str]]], header: str | None = None
    ) -> None:
        """Write variables to an env file, preserving comments."""
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            if header:
                f.write(header + "\n\n")

            for var_name, (value, comments) in variables.items():
                # Write preceding comments
                for comment in comments:
                    f.write(comment + "\n")
                # Write the variable
                f.write(f"{var_name}={value}\n")

    def migrate_feature_branch(self, dry_run: bool = False) -> bool:
        """
        Migrate from feature branch environments-enabled/ structure.

        Feature branch layout:
          environments-available/*.template       -> templates (backed up and removed)
          environments-enabled/onramp.env         -> services-enabled/.env (global)
          environments-enabled/onramp-external.env -> services-enabled/.env.external
          environments-enabled/onramp-nfs.env     -> services-enabled/.env.nfs
          environments-enabled/{service}.env      -> services-enabled/{service}.env

        Handles cases where:
        - Only templates exist (no env files generated yet)
        - Only env files exist (templates already cleaned up)
        - Both exist (full feature branch state)
        """
        print("Starting migration from feature branch...")

        # Check what exists
        has_env_dir = self.environments_enabled.exists()
        has_env_files = has_env_dir and any(self.environments_enabled.glob("*.env"))
        has_templates = self.environments_available.exists() and any(
            self.environments_available.glob("*.template")
        )

        if has_templates:
            template_count = len(list(self.environments_available.glob("*.template")))
            print(f"  Found {template_count} template files in environments-available/")

        # Track files to migrate
        migrations: list[tuple[Path, Path, str]] = []  # (source, dest, description)

        # Process all .env files if they exist
        if has_env_files:
            for env_file in sorted(self.environments_enabled.glob("*.env")):
                stem = env_file.stem

                if stem == "onramp":
                    # Global config -> .env
                    dest = self.services_enabled / ".env"
                    migrations.append((env_file, dest, "global config"))
                elif stem in FEATURE_BRANCH_SPECIAL_FILES:
                    # Special files like onramp-external -> .env.external
                    dest_name = FEATURE_BRANCH_SPECIAL_FILES[stem]
                    dest = self.services_enabled / dest_name
                    migrations.append((env_file, dest, f"special config ({dest_name})"))
                else:
                    # Service-specific files -> {service}.env
                    dest = self.services_enabled / f"{stem}.env"
                    migrations.append((env_file, dest, f"service config ({stem})"))

            print(f"  Found {len(migrations)} environment files to migrate:")
            for source, dest, desc in migrations:
                print(f"    {source.name} -> {dest.name} ({desc})")
        else:
            print("  No environment files found in environments-enabled/")
            if has_templates:
                print("  Will clean up templates directory only")

        if dry_run:
            print("\nDry run - no changes made")
            return True

        # Create backup directory
        self.backups_dir.mkdir(parents=True, exist_ok=True)

        # Perform env file migrations if any
        if migrations:
            # Create services-enabled directory
            self.services_enabled.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for source, dest, desc in migrations:
                content = source.read_text()
                header = f"# OnRamp Configuration\n# Migrated from feature branch on {timestamp}\n# Original: {source.name}\n"

                with open(dest, "w") as f:
                    f.write(header)
                    f.write("\n")
                    f.write(content)

                print(f"  Created: {dest.name}")

        # Backup and remove environments-enabled/ if it exists
        if has_env_dir:
            backup_path = self.backups_dir / "environments-enabled.legacy"
            if backup_path.exists():
                shutil.rmtree(backup_path)
            shutil.copytree(self.environments_enabled, backup_path)
            print(f"  Backed up: environments-enabled/ -> backups/environments-enabled.legacy/")

            shutil.rmtree(self.environments_enabled)
            print("  Removed: environments-enabled/")

        # Clean up environments-available/ templates if they exist
        if has_templates:
            templates_backup = self.backups_dir / "environments-available.legacy"
            if templates_backup.exists():
                shutil.rmtree(templates_backup)
            shutil.copytree(self.environments_available, templates_backup)
            print(f"  Backed up: environments-available/ -> backups/environments-available.legacy/")

            shutil.rmtree(self.environments_available)
            print("  Removed: environments-available/")

        print("\nMigration complete!")
        return True

    def migrate_legacy(self, dry_run: bool = False) -> bool:
        """Migrate from legacy monolithic .env file."""
        print("Starting migration from legacy .env...")

        # Parse the legacy env file
        all_vars = self.parse_env_file(self.legacy_env)
        print(f"  Found {len(all_vars)} variables")

        # Sort variables into buckets
        global_vars: dict[str, tuple[str, list[str]]] = {}
        service_vars: dict[str, dict[str, tuple[str, list[str]]]] = {}
        custom_vars: dict[str, tuple[str, list[str]]] = {}

        for var_name, var_data in all_vars.items():
            service = self.get_service_for_var(var_name)

            if service is None and var_name in GLOBAL_VARS:
                global_vars[var_name] = var_data
            elif service:
                if service not in service_vars:
                    service_vars[service] = {}
                service_vars[service][var_name] = var_data
            else:
                custom_vars[var_name] = var_data

        print(f"  Global vars: {len(global_vars)}")
        print(f"  Service-specific vars: {sum(len(v) for v in service_vars.values())} across {len(service_vars)} services")
        print(f"  Custom/unmapped vars: {len(custom_vars)}")

        if dry_run:
            print("\nDry run - no changes made")
            print("\nGlobal vars would be written to services-enabled/.env:")
            for var in sorted(global_vars.keys()):
                print(f"  {var}")
            print("\nService vars:")
            for service, svars in sorted(service_vars.items()):
                print(f"  {service}.env: {', '.join(sorted(svars.keys()))}")
            if custom_vars:
                print("\nCustom vars would be written to services-enabled/custom.env:")
                for var in sorted(custom_vars.keys()):
                    print(f"  {var}")
            return True

        # Create services-enabled directory
        self.services_enabled.mkdir(parents=True, exist_ok=True)

        # Write global config
        if global_vars:
            header = "# OnRamp Global Configuration\n# Migrated from legacy .env on " + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.write_env_file(self.services_enabled / ".env", global_vars, header)
            print(f"  Created: services-enabled/.env ({len(global_vars)} vars)")

        # Write service-specific configs
        for service, svars in service_vars.items():
            header = f"# {service.upper()} Configuration\n# Migrated from legacy .env on " + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.write_env_file(self.services_enabled / f"{service}.env", svars, header)
            print(f"  Created: services-enabled/{service}.env ({len(svars)} vars)")

        # Write unmapped variables to custom.env
        if custom_vars:
            header = "# Custom/Unmapped Variables\n# Migrated from legacy .env on " + datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            self.write_env_file(self.services_enabled / "custom.env", custom_vars, header)
            print(f"  Created: services-enabled/custom.env ({len(custom_vars)} vars)")

        # Backup and remove legacy .env
        self.backups_dir.mkdir(parents=True, exist_ok=True)
        backup_path = self.backups_dir / ".env.legacy"
        shutil.copy2(self.legacy_env, backup_path)
        print(f"  Backed up: .env -> {backup_path}")

        self.legacy_env.unlink()
        print("  Removed: .env")

        print("\nMigration complete!")
        return True

    def migrate(self, dry_run: bool = False) -> bool:
        """Route to appropriate migration based on detected source."""
        if (self.services_enabled / ".env").exists():
            print("services-enabled/.env already exists. Migration already complete.")
            return True
        if self.should_migrate_feature_branch():
            return self.migrate_feature_branch(dry_run)
        if self.should_migrate_legacy():
            return self.migrate_legacy(dry_run)
        print("No migration source found (.env or environments-enabled/).")
        return True


def main():
    parser = argparse.ArgumentParser(
        description="Migrate legacy .env to modular environment system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  migrate-env.py                Run migration if needed
  migrate-env.py --dry-run      Show what would be migrated without making changes
  migrate-env.py --force        Run migration even if services-enabled/.env exists
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be migrated without making changes",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Run migration even if services-enabled/.env exists",
    )
    parser.add_argument(
        "--base-dir",
        default="/app",
        help="Base directory (default: /app)",
    )

    args = parser.parse_args()

    migrator = EnvMigrator(args.base_dir)

    if args.force:
        # Remove existing to force migration
        target = migrator.services_enabled / ".env"
        if target.exists():
            target.unlink()

    success = migrator.migrate(dry_run=args.dry_run)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
