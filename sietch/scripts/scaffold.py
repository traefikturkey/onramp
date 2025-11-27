#!/usr/bin/env python
"""
scaffold.py - Convention-based scaffolding for OnRamp services

Handles building and tearing down service configurations based on templates
in the services-scaffold/ directory.

Conventions:
- *.template files are rendered with envsubst -> output location
- *.static files are copied without modification
- Subdirectories are mirrored in the output

Output mapping:
- services-scaffold/onramp/.env.template -> services-enabled/.env
- services-scaffold/onramp/.env.<stub>.template -> services-enabled/.env.<stub>
- services-scaffold/<service>/env.template -> services-enabled/<service>.env
- services-scaffold/<service>/<file>.template -> etc/<service>/<file>
- services-scaffold/<service>/<file>.static -> etc/<service>/<file>
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


class Scaffolder:
    """Handles scaffolding operations for services."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.scaffold_dir = self.base_dir / "services-scaffold"
        self.services_enabled = self.base_dir / "services-enabled"
        self.etc_dir = self.base_dir / "etc"

    def find_scaffold_files(self, service: str) -> tuple[list[Path], list[Path]]:
        """Find all template and static files for a service."""
        service_scaffold = self.scaffold_dir / service
        if not service_scaffold.exists():
            return [], []

        templates = list(service_scaffold.rglob("*.template"))
        statics = list(service_scaffold.rglob("*.static"))
        return templates, statics

    def has_scaffold(self, service: str) -> bool:
        """Check if a service has scaffold files."""
        templates, statics = self.find_scaffold_files(service)
        return bool(templates or statics)

    def get_output_path(self, service: str, source: Path) -> Path:
        """Determine output path for a scaffold file."""
        relative = source.relative_to(self.scaffold_dir / service)
        # Remove .template or .static suffix
        output_name = source.stem if source.suffix in (".template", ".static") else source.name

        # Handle special cases for onramp (global config)
        if service == "onramp":
            if output_name.startswith(".env"):
                return self.services_enabled / output_name
            # Other onramp files go to etc/onramp
            return self.etc_dir / "onramp" / relative.parent / output_name

        # env.template -> services-enabled/<service>.env
        if relative.name == "env.template":
            return self.services_enabled / f"{service}.env"

        # All other files go to etc/<service>/
        return self.etc_dir / service / relative.parent / output_name

    def render_template(self, source: Path, dest: Path) -> bool:
        """Render a template file using envsubst."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(source, "r") as f:
                template_content = f.read()

            result = subprocess.run(
                ["envsubst"],
                input=template_content,
                capture_output=True,
                text=True,
                check=True,
            )

            with open(dest, "w") as f:
                f.write(result.stdout)

            print(f"  Rendered: {source.name} -> {dest}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"  Error rendering {source}: {e.stderr}", file=sys.stderr)
            return False
        except Exception as e:
            print(f"  Error rendering {source}: {e}", file=sys.stderr)
            return False

    def copy_static(self, source: Path, dest: Path) -> bool:
        """Copy a static file without modification."""
        try:
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Only copy if dest doesn't exist (no-clobber behavior)
            if not dest.exists():
                shutil.copy2(source, dest)
                print(f"  Copied: {source.name} -> {dest}")
            else:
                print(f"  Skipped (exists): {dest}")
            return True
        except Exception as e:
            print(f"  Error copying {source}: {e}", file=sys.stderr)
            return False

    def build(self, service: str) -> bool:
        """Build scaffold for a service."""
        if not self.has_scaffold(service):
            print(f"No scaffold files found for '{service}'")
            return True

        print(f"Building scaffold for '{service}'...")
        templates, statics = self.find_scaffold_files(service)
        success = True

        for template in templates:
            dest = self.get_output_path(service, template)
            if not self.render_template(template, dest):
                success = False

        for static in statics:
            dest = self.get_output_path(service, static)
            if not self.copy_static(static, dest):
                success = False

        return success

    def teardown(self, service: str, preserve_etc: bool = True) -> bool:
        """Tear down scaffold for a service."""
        print(f"Tearing down scaffold for '{service}'...")

        # Remove service.env from services-enabled
        env_file = self.services_enabled / f"{service}.env"
        if env_file.exists():
            env_file.unlink()
            print(f"  Removed: {env_file}")

        # Optionally remove etc/<service>
        if not preserve_etc:
            etc_service = self.etc_dir / service
            if etc_service.exists():
                shutil.rmtree(etc_service)
                print(f"  Removed directory: {etc_service}")

        return True

    def build_all_enabled(self) -> bool:
        """Build scaffolds for all enabled services."""
        success = True

        # Always build onramp globals first
        if self.has_scaffold("onramp"):
            if not self.build("onramp"):
                success = False

        # Build for each enabled service
        for service_yml in self.services_enabled.glob("*.yml"):
            service = service_yml.stem
            if self.has_scaffold(service):
                if not self.build(service):
                    success = False

        return success

    def list_scaffolds(self) -> list[str]:
        """List all available scaffolds."""
        if not self.scaffold_dir.exists():
            return []
        return sorted(d.name for d in self.scaffold_dir.iterdir() if d.is_dir())


def main():
    parser = argparse.ArgumentParser(
        description="Convention-based scaffolding for OnRamp services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scaffold.py build adguard        Build scaffold for adguard
  scaffold.py build --all          Build scaffolds for all enabled services
  scaffold.py teardown adguard     Remove service env file (preserve etc/)
  scaffold.py nuke adguard         Remove service env and etc/ directory
  scaffold.py list                 List available scaffolds
  scaffold.py check adguard        Check if service has scaffold files
        """,
    )

    parser.add_argument(
        "action",
        choices=["build", "teardown", "nuke", "list", "check"],
        help="Action to perform",
    )
    parser.add_argument(
        "service",
        nargs="?",
        help="Service name (required for build/teardown/nuke/check)",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Build scaffolds for all enabled services",
    )
    parser.add_argument(
        "--base-dir",
        default="/app",
        help="Base directory (default: /app)",
    )

    args = parser.parse_args()

    scaffolder = Scaffolder(args.base_dir)

    if args.action == "list":
        scaffolds = scaffolder.list_scaffolds()
        if scaffolds:
            print("Available scaffolds:")
            for s in scaffolds:
                print(f"  {s}")
        else:
            print("No scaffolds found in services-scaffold/")
        return 0

    if args.action == "build" and args.all:
        success = scaffolder.build_all_enabled()
        return 0 if success else 1

    if args.action in ("build", "teardown", "nuke", "check") and not args.service:
        parser.error(f"Service name required for '{args.action}' action")

    if args.action == "check":
        has_scaffold = scaffolder.has_scaffold(args.service)
        if has_scaffold:
            print(f"Service '{args.service}' has scaffold files")
            return 0
        else:
            print(f"Service '{args.service}' has no scaffold files")
            return 1

    if args.action == "build":
        success = scaffolder.build(args.service)
        return 0 if success else 1

    if args.action == "teardown":
        success = scaffolder.teardown(args.service, preserve_etc=True)
        return 0 if success else 1

    if args.action == "nuke":
        success = scaffolder.teardown(args.service, preserve_etc=False)
        return 0 if success else 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
