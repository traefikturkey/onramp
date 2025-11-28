#!/usr/bin/env python
"""
scaffold.py - Convention-based scaffolding for OnRamp services

Handles building and tearing down service configurations based on templates
in the services-scaffold/ directory.

Conventions:
- *.template files are rendered with envsubst -> output location
- scaffold.yml manifests define complex operations (key gen, downloads, etc.)
- All other files are copied as-is (except ignored patterns)
- Subdirectories are mirrored in the output

Ignored patterns (not copied):
- *.md (documentation)
- .gitkeep (git placeholders)
- scaffold.yml (manifest file)

Output mapping:
- services-scaffold/onramp/.env.template -> services-enabled/.env
- services-scaffold/onramp/.env.<stub>.template -> services-enabled/.env.<stub>
- services-scaffold/<service>/env.template -> services-enabled/<service>.env
- services-scaffold/<service>/<file>.template -> etc/<service>/<file>
- services-scaffold/<service>/<file> -> etc/<service>/<file>
"""

import argparse
import fnmatch
import os
import shutil
import subprocess
import sys
from pathlib import Path

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

# Import operations module for manifest execution
try:
    from operations import OperationContext, execute_operation

    OPERATIONS_AVAILABLE = True
except ImportError:
    OPERATIONS_AVAILABLE = False

# Files/patterns to ignore when copying static files
IGNORE_PATTERNS = [
    "*.md",
    ".gitkeep",
    "scaffold.yml",
]


class Scaffolder:
    """Handles scaffolding operations for services."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.scaffold_dir = self.base_dir / "services-scaffold"
        self.services_enabled = self.base_dir / "services-enabled"
        self.etc_dir = self.base_dir / "etc"

    def _should_ignore(self, path: Path) -> bool:
        """Check if a file should be ignored (not copied)."""
        name = path.name
        for pattern in IGNORE_PATTERNS:
            if fnmatch.fnmatch(name, pattern):
                return True
        return False

    def find_scaffold_files(self, service: str) -> tuple[list[Path], list[Path]]:
        """Find all template and static files for a service."""
        service_scaffold = self.scaffold_dir / service
        if not service_scaffold.exists():
            return [], []

        templates = list(service_scaffold.rglob("*.template"))

        # Static files: everything except templates and ignored patterns
        statics = [
            f
            for f in service_scaffold.rglob("*")
            if f.is_file() and f.suffix != ".template" and not self._should_ignore(f)
        ]

        return templates, statics

    def find_manifest(self, service: str) -> Path | None:
        """Find scaffold.yml manifest for a service."""
        manifest = self.scaffold_dir / service / "scaffold.yml"
        return manifest if manifest.exists() else None

    def has_scaffold(self, service: str) -> bool:
        """Check if a service has scaffold files or manifest."""
        templates, statics = self.find_scaffold_files(service)
        manifest = self.find_manifest(service)
        return bool(templates or statics or manifest)

    def get_output_path(self, service: str, source: Path) -> Path:
        """Determine output path for a scaffold file."""
        relative = source.relative_to(self.scaffold_dir / service)

        # Only strip .template suffix (not .static anymore)
        if source.suffix == ".template":
            output_name = source.stem
        else:
            output_name = source.name

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

    def execute_manifest(self, service: str) -> bool:
        """Execute operations from scaffold.yml manifest."""
        manifest_path = self.find_manifest(service)
        if not manifest_path:
            return True  # No manifest is not an error

        if not YAML_AVAILABLE:
            print(f"  Warning: pyyaml not installed, skipping manifest for {service}")
            return True

        if not OPERATIONS_AVAILABLE:
            print(f"  Warning: operations module not available, skipping manifest for {service}")
            return True

        print(f"  Executing manifest operations...")

        try:
            with open(manifest_path, "r") as f:
                manifest = yaml.safe_load(f)
        except Exception as e:
            print(f"  Error reading manifest: {e}", file=sys.stderr)
            return False

        # Validate version
        version = manifest.get("version", "1")
        if version != "1":
            print(f"  Unsupported manifest version: {version}", file=sys.stderr)
            return False

        # Create context
        ctx = OperationContext(
            service=service,
            base_dir=self.base_dir,
            scaffold_dir=self.scaffold_dir,
            etc_dir=self.etc_dir,
            services_enabled=self.services_enabled,
        )

        # Execute operations in order
        operations = manifest.get("operations", [])
        for i, op_config in enumerate(operations, 1):
            op_type = op_config.get("type", "unknown")
            if not execute_operation(op_config, ctx):
                print(f"  Failed at operation {i}: {op_type}", file=sys.stderr)
                return False

        return True

    def build(self, service: str) -> bool:
        """Build scaffold for a service."""
        if not self.has_scaffold(service):
            print(f"No scaffold files found for '{service}'")
            return True

        print(f"Building scaffold for '{service}'...")
        templates, statics = self.find_scaffold_files(service)
        success = True

        # Phase 1: Render templates
        for template in templates:
            dest = self.get_output_path(service, template)
            if not self.render_template(template, dest):
                success = False

        # Phase 2: Copy static files
        for static in statics:
            dest = self.get_output_path(service, static)
            if not self.copy_static(static, dest):
                success = False

        # Phase 3: Execute manifest operations (after templates/statics)
        if not self.execute_manifest(service):
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
