#!/usr/bin/env python
"""
services.py - Service listing and metadata management for OnRamp

Commands:
  list [--enabled|--available|--games|--overrides|--external|--all]
  info <service>
  count [--enabled|--available]
  markdown
  validate <service>
  archive-env <service> - Archive a service's .env file to services-enabled/archive/
  restore-env <service> - Restore a service's .env file from archive (interactive)
  check-archive <service> - Check if archived .env exists for a service
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path


class ServiceManager:
    """Manages service discovery and metadata."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.services_available = self.base_dir / "services-available"
        self.services_enabled = self.base_dir / "services-enabled"
        self.overrides_available = self.base_dir / "overrides-available"
        self.overrides_enabled = self.base_dir / "overrides-enabled"
        self.games_dir = self.services_available / "games"
        self.external_dir = self.base_dir / "external-available"
        self.archive_dir = self.services_enabled / "archive"

    def _strip_extension(self, filename: str) -> str:
        """Remove .yml extension from filename."""
        return filename.rsplit(".yml", 1)[0] if filename.endswith(".yml") else filename

    def _parse_metadata(self, yml_path: Path) -> dict:
        """Parse metadata from comment lines in YAML files."""
        metadata = {
            "description": None,
            "url": None,
            "category": None,
            "skip_services_file": False,
        }

        try:
            with open(yml_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    # Parse all comment lines in the file
                    if not line.startswith("#"):
                        continue

                    if line.startswith("# description:"):
                        metadata["description"] = line.split(":", 1)[1].strip()
                    elif line.startswith("# category:"):
                        metadata["category"] = line.split(":", 1)[1].strip()
                    elif line.startswith("# skip_services_file:"):
                        val = line.split(":", 1)[1].strip().lower()
                        metadata["skip_services_file"] = val in ("true", "yes", "1")
                    elif line.startswith("# http"):
                        metadata["url"] = line[2:].strip()
        except Exception:
            pass

        return metadata

    def list_available(self) -> list[str]:
        """List all available services."""
        if not self.services_available.exists():
            return []
        services = []
        for f in self.services_available.iterdir():
            if f.is_file() and f.suffix == ".yml":
                services.append(self._strip_extension(f.name))
        return sorted(services)

    def list_enabled(self) -> list[str]:
        """List all enabled services."""
        if not self.services_enabled.exists():
            return []
        services = []
        for f in self.services_enabled.iterdir():
            if f.is_file() and f.suffix == ".yml":
                services.append(self._strip_extension(f.name))
        return sorted(services)

    def list_games(self) -> list[str]:
        """List all available games."""
        if not self.games_dir.exists():
            return []
        games = []
        for f in self.games_dir.iterdir():
            if f.is_file() and f.suffix == ".yml":
                games.append(self._strip_extension(f.name))
        return sorted(games)

    def list_overrides(self) -> list[str]:
        """List all available overrides."""
        if not self.overrides_available.exists():
            return []
        overrides = []
        for f in self.overrides_available.iterdir():
            if f.is_file() and f.suffix == ".yml":
                overrides.append(self._strip_extension(f.name))
        return sorted(overrides)

    def list_external(self) -> list[str]:
        """List all available external services."""
        if not self.external_dir.exists():
            return []
        external = []
        for f in self.external_dir.iterdir():
            if f.is_file() and f.suffix == ".yml":
                external.append(self._strip_extension(f.name))
        return sorted(external)

    def get_service_info(self, service: str) -> dict | None:
        """Get detailed info for a service."""
        # Check available services
        yml_path = self.services_available / f"{service}.yml"
        if not yml_path.exists():
            # Check games
            yml_path = self.games_dir / f"{service}.yml"
            if not yml_path.exists():
                return None

        metadata = self._parse_metadata(yml_path)
        is_enabled = (self.services_enabled / f"{service}.yml").exists()
        has_env = (self.services_enabled / f"{service}.env").exists()
        has_etc = (self.base_dir / "etc" / service).exists()

        return {
            "name": service,
            "enabled": is_enabled,
            "has_env": has_env,
            "has_etc": has_etc,
            "yml_path": str(yml_path),
            **metadata,
        }

    def validate_service(self, service: str) -> tuple[bool, list[str]]:
        """Validate a service configuration. Returns (valid, errors)."""
        errors = []
        info = self.get_service_info(service)

        if not info:
            return False, [f"Service '{service}' not found"]

        # Check if enabled service has required files
        if info["enabled"]:
            yml_path = self.services_enabled / f"{service}.yml"
            if not yml_path.exists() and not yml_path.is_symlink():
                errors.append(f"Enabled but missing symlink: {yml_path}")

        return len(errors) == 0, errors

    def generate_markdown(self) -> str:
        """Generate SERVICES.md content."""
        lines = ["# Available Services", ""]

        # Group by category
        categories = {}
        for service in self.list_available():
            yml_path = self.services_available / f"{service}.yml"
            metadata = self._parse_metadata(yml_path)

            if metadata.get("skip_services_file"):
                continue

            category = metadata.get("category") or "uncategorized"
            if category not in categories:
                categories[category] = []

            categories[category].append(
                {
                    "name": service,
                    "description": metadata.get("description"),
                    "url": metadata.get("url"),
                }
            )

        # Output by category
        for category in sorted(categories.keys()):
            lines.append(f"## {category.title()}")
            lines.append("")
            lines.append("| Service | Description |")
            lines.append("|---------|-------------|")

            for svc in sorted(categories[category], key=lambda x: x["name"]):
                name = svc["name"]
                if svc["url"]:
                    name = f"[{name}]({svc['url']})"
                desc = svc["description"] or ""
                lines.append(f"| {name} | {desc} |")

            lines.append("")

        # Games section
        games = self.list_games()
        if games:
            lines.append("## Available Games")
            lines.append("")
            lines.append("| Game | Description |")
            lines.append("|------|-------------|")

            for game in games:
                yml_path = self.games_dir / f"{game}.yml"
                metadata = self._parse_metadata(yml_path)
                name = game
                if metadata.get("url"):
                    name = f"[{game}]({metadata['url']})"
                desc = metadata.get("description") or ""
                lines.append(f"| {name} | {desc} |")

            lines.append("")

        return "\n".join(lines)

    def archive_env(self, service: str) -> tuple[bool, str]:
        """Archive a service's .env file to the archive directory.
        
        Returns (success, message).
        """
        env_file = self.services_enabled / f"{service}.env"
        
        if not env_file.exists():
            return False, f"No .env file found for service '{service}'"
        
        # Ensure archive directory exists
        self.archive_dir.mkdir(exist_ok=True)
        
        archive_file = self.archive_dir / f"{service}.env"
        
        try:
            shutil.move(str(env_file), str(archive_file))
            return True, f"Archived {service}.env to {archive_file}"
        except Exception as e:
            return False, f"Failed to archive {service}.env: {e}"

    def check_archive(self, service: str) -> bool:
        """Check if an archived .env file exists for a service."""
        archive_file = self.archive_dir / f"{service}.env"
        return archive_file.exists()

    def restore_env(self, service: str, interactive: bool = True) -> tuple[bool, str]:
        """Restore a service's .env file from the archive.
        
        If interactive=True, prompts user before restoring.
        Returns (success, message).
        """
        archive_file = self.archive_dir / f"{service}.env"
        
        if not archive_file.exists():
            return False, f"No archived .env file found for service '{service}'"
        
        env_file = self.services_enabled / f"{service}.env"
        
        # Check if destination already exists
        if env_file.exists():
            if interactive:
                response = input(
                    f"⚠️  {service}.env already exists. Overwrite with archived version? [y/N]: "
                )
                if response.lower() not in ("y", "yes"):
                    return False, "Restore cancelled by user"
            else:
                return False, f"{service}.env already exists (use --force to overwrite)"
        
        try:
            shutil.copy2(str(archive_file), str(env_file))
            return True, f"Restored {service}.env from archive"
        except Exception as e:
            return False, f"Failed to restore {service}.env: {e}"

    def list_archived(self) -> list[str]:
        """List all archived .env files."""
        if not self.archive_dir.exists():
            return []
        
        archived = []
        for f in self.archive_dir.iterdir():
            if f.is_file() and f.suffix == ".env":
                archived.append(self._strip_extension(f.name))
        return sorted(archived)


def main():
    parser = argparse.ArgumentParser(
        description="Service listing and metadata management",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "action",
        choices=["list", "info", "count", "markdown", "validate", "archive-env", "restore-env", "check-archive"],
        help="Action to perform",
    )
    parser.add_argument("service", nargs="?", help="Service name (for info/validate/archive/restore)")
    parser.add_argument(
        "--enabled", action="store_true", help="List/count enabled services"
    )
    parser.add_argument(
        "--available", action="store_true", help="List/count available services"
    )
    parser.add_argument("--games", action="store_true", help="List games")
    parser.add_argument("--overrides", action="store_true", help="List overrides")
    parser.add_argument(
        "--external", action="store_true", help="List external services"
    )
    parser.add_argument("--all", action="store_true", help="List all categories")
    parser.add_argument("--archived", action="store_true", help="List archived .env files")
    parser.add_argument("--no-interactive", action="store_true", help="Disable interactive prompts")
    parser.add_argument(
        "--base-dir", default="/app", help="Base directory (default: /app)"
    )

    args = parser.parse_args()
    mgr = ServiceManager(args.base_dir)

    if args.action == "list":
        # Default to --available if no filter specified
        if not any(
            [
                args.enabled,
                args.available,
                args.games,
                args.overrides,
                args.external,
                args.archived,
                args.all,
            ]
        ):
            args.available = True

        if args.all:
            args.available = args.enabled = args.games = args.overrides = (
                args.external
            ) = args.archived = True

        if args.available:
            for s in mgr.list_available():
                print(s)
        if args.enabled:
            if args.available:
                print("\n--- Enabled ---")
            for s in mgr.list_enabled():
                print(s)
        if args.games:
            if args.available or args.enabled:
                print("\n--- Games ---")
            for s in mgr.list_games():
                print(s)
        if args.overrides:
            if args.available or args.enabled or args.games:
                print("\n--- Overrides ---")
            for s in mgr.list_overrides():
                print(s)
        if args.external:
            if args.available or args.enabled or args.games or args.overrides:
                print("\n--- External ---")
            for s in mgr.list_external():
                print(s)
        if args.archived:
            if args.available or args.enabled or args.games or args.overrides or args.external:
                print("\n--- Archived .env Files ---")
            for s in mgr.list_archived():
                print(s)
        return 0

    if args.action == "count":
        if args.enabled:
            print(len(mgr.list_enabled()))
        else:
            print(len(mgr.list_available()))
        return 0

    if args.action == "info":
        if not args.service:
            parser.error("Service name required for 'info' action")
        info = mgr.get_service_info(args.service)
        if not info:
            print(f"Service '{args.service}' not found", file=sys.stderr)
            return 1
        for k, v in info.items():
            print(f"{k}: {v}")
        return 0

    if args.action == "validate":
        if not args.service:
            parser.error("Service name required for 'validate' action")
        valid, errors = mgr.validate_service(args.service)
        if valid:
            print(f"Service '{args.service}' is valid")
            return 0
        else:
            print(f"Service '{args.service}' has errors:", file=sys.stderr)
            for err in errors:
                print(f"  - {err}", file=sys.stderr)
            return 1

    if args.action == "markdown":
        print(mgr.generate_markdown())
        return 0

    if args.action == "archive-env":
        if not args.service:
            parser.error("Service name required for 'archive-env' action")
        success, message = mgr.archive_env(args.service)
        print(message)
        return 0 if success else 1

    if args.action == "restore-env":
        if not args.service:
            parser.error("Service name required for 'restore-env' action")
        interactive = not args.no_interactive
        success, message = mgr.restore_env(args.service, interactive=interactive)
        print(message)
        return 0 if success else 1

    if args.action == "check-archive":
        if not args.service:
            parser.error("Service name required for 'check-archive' action")
        exists = mgr.check_archive(args.service)
        if exists:
            print(f"yes")
            return 0
        else:
            print(f"no")
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
