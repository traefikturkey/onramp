#!/usr/bin/env python
"""
enable_service.py - Service dependency resolution wizard for OnRamp

Handles enabling services with automatic dependency resolution and optional
service prompts. Recursively processes dependencies and prompts for optional
services/groups.

Commands:
  enable <service> - Enable a service with dependency resolution wizard
"""

import argparse
import sys
from pathlib import Path

from services import ServiceManager
from scaffold import Scaffolder


class EnableServiceWizard:
    """Wizard for enabling services with dependency resolution."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.services_available = self.base_dir / "services-available"
        self.services_enabled = self.base_dir / "services-enabled"
        self.manager = ServiceManager(base_dir)
        self.scaffolder = Scaffolder(base_dir)
        self.enabled_this_session: set[str] = set()

    def _is_enabled(self, service: str) -> bool:
        """Check if service is already enabled."""
        return service in self.manager.list_enabled()

    def _prompt_yes_no(self, question: str, default: bool = False) -> bool:
        """Prompt user for yes/no answer.

        Args:
            question: Question to ask user
            default: Default answer if user presses enter or if non-TTY

        Returns:
            True for yes, False for no
        """
        default_text = "Y/n" if default else "y/N"
        try:
            response = input(f"{question} [{default_text}]: ").strip().lower()
            if not response:
                return default
            return response in ("y", "yes")
        except (EOFError, KeyboardInterrupt):
            # Non-TTY context or user interrupted, use default
            return default

    def _do_enable(self, service: str) -> bool:
        """Actually enable a single service (symlink + archive check + scaffold).

        Args:
            service: Service name to enable

        Returns:
            True if successful, False otherwise
        """
        # Check if service exists
        service_yml = self.services_available / f"{service}.yml"
        if not service_yml.exists():
            print(f"Error: Service '{service}' not found in services-available")
            return False

        # Create symlink
        symlink_dest = self.services_enabled / f"{service}.yml"
        try:
            if not symlink_dest.exists():
                symlink_dest.symlink_to(service_yml)
                print(f"  Enabled service: {service}")
        except Exception as e:
            print(f"Error: Failed to create symlink for {service}: {e}")
            return False

        # Check for archived .env and restore if exists
        if self.manager.check_archive(service):
            print(f"  Found archived .env for {service}")
            success, message = self.manager.restore_env(service, interactive=True)
            print(f"  {message}")

        # Run scaffolding
        try:
            print(f"  Scaffolding {service}...")
            if not self.scaffolder.build(service):
                print(f"Error: Scaffolding failed for {service}")
                return False
        except Exception as e:
            print(f"Error: Exception during scaffolding for {service}: {e}")
            return False

        print(f"Successfully enabled {service}")
        return True

    def enable_service(self, service: str, _is_root: bool = True) -> bool:
        """Main entry point - enable a service with dependency resolution.

        Args:
            service: Service name to enable
            _is_root: Internal flag - True if this is the top-level call (not recursive)

        Returns:
            True if successful (including if already enabled), False on error
        """
        # Check if already enabled OR already processed this session
        if self._is_enabled(service):
            if _is_root:
                print(f"Service '{service}' is already enabled")
            return True

        if service in self.enabled_this_session:
            return True

        # Add to tracking to prevent loops
        self.enabled_this_session.add(service)

        # Check if service exists
        service_yml = self.services_available / f"{service}.yml"
        if not service_yml.exists():
            print(f"Error: Service '{service}' not found in services-available")
            print(f"  Run 'make list-services' to see available services")
            return False

        # Get external dependencies
        dependencies = self.manager.get_depends_on(service)
        deps_to_enable = [dep for dep in dependencies if not self._is_enabled(dep)]

        # Enable dependencies first
        if deps_to_enable:
            if _is_root:
                print(f"\n=== Resolving Dependencies for {service} ===")
            for dep in deps_to_enable:
                print(f"  Enabling required dependency: {dep}")
                if not self.enable_service(dep, _is_root=False):
                    print(f"Error: Failed to enable required dependency '{dep}'")
                    print(f"  Cannot enable '{service}' without its dependencies.")
                    print(f"  To retry: make enable-service {dep}")
                    return False

        # Get metadata for optional services/groups
        metadata = self.manager._parse_metadata(service_yml)
        has_optionals = metadata.get("optional_groups") or metadata.get("optional_services")

        if has_optionals and _is_root:
            print(f"\n=== Optional Services for {service} ===")

        # Process optional groups
        for group in metadata.get("optional_groups", []):
            group_name = group.get("name", "Unknown")
            group_prompt = group.get("prompt", f"Enable {group_name}?")
            group_services = group.get("services", [])

            if self._prompt_yes_no(group_prompt, default=False):
                for group_service in group_services:
                    if not self.enable_service(group_service, _is_root=False):
                        print(f"Warning: Failed to enable optional service '{group_service}' from group '{group_name}'")

        # Process optional services
        for opt_service in metadata.get("optional_services", []):
            service_name = opt_service.get("service")
            service_prompt = opt_service.get("prompt", f"Enable {service_name}?")

            if self._prompt_yes_no(service_prompt, default=False):
                if not self.enable_service(service_name, _is_root=False):
                    print(f"Warning: Failed to enable optional service '{service_name}'")

        # Finally, enable this service
        if _is_root:
            print(f"\n=== Enabling {service} ===")

        success = self._do_enable(service)

        # Show completion summary for root call
        if success and _is_root and len(self.enabled_this_session) > 1:
            print(f"\n=== Summary ===")
            print(f"Services enabled this session:")
            for s in sorted(self.enabled_this_session):
                print(f"  - {s}")

        return success


def main():
    parser = argparse.ArgumentParser(
        description="Service dependency resolution wizard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  enable_service.py enable traefik       Enable traefik with dependency resolution
  enable_service.py enable adguard       Enable adguard and prompt for optional services
        """,
    )

    parser.add_argument(
        "action",
        choices=["enable"],
        help="Action to perform",
    )
    parser.add_argument(
        "service",
        help="Service name to enable",
    )
    parser.add_argument(
        "--base-dir",
        default="/app",
        help="Base directory (default: /app)",
    )

    args = parser.parse_args()
    wizard = EnableServiceWizard(args.base_dir)

    if args.action == "enable":
        success = wizard.enable_service(args.service)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
