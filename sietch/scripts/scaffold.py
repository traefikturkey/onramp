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
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.command import CommandExecutor

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
    "MESSAGE.txt",
]


class Scaffolder:
    """Handles scaffolding operations for services."""

    def __init__(
        self,
        base_dir: str = "/app",
        executor: "CommandExecutor | None" = None,
    ):
        self.base_dir = Path(base_dir)
        self.scaffold_dir = self.base_dir / "services-scaffold"
        self.services_enabled = self.base_dir / "services-enabled"
        self.services_available = self.base_dir / "services-available"
        self.etc_dir = self.base_dir / "etc"

        # Use injected executor or create default
        if executor is not None:
            self._executor = executor
        else:
            from adapters.subprocess_cmd import SubprocessCommandExecutor

            self._executor = SubprocessCommandExecutor()

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

            result = self._executor.run(
                ["envsubst"],
                input=template_content,
                capture_output=True,
                check=True,
            )

            if result.returncode != 0:
                print(f"  Error rendering {source}: {result.stderr}", file=sys.stderr)
                return False

            with open(dest, "w") as f:
                f.write(result.stdout)

            print(f"  Rendered: {source.name} -> {dest}")
            return True
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

    def create_etc_volumes(self, service: str, scaffold_statics: list[Path] = None) -> bool:
        """Create etc/ volume directories/files from service YAML.

        Parses the docker-compose YAML to find volume mounts pointing to
        ./etc/<service>/* and creates the necessary directories or files.

        Args:
            service: Service name
            scaffold_statics: List of static files from scaffold that will be copied
        """
        import re

        # Build set of paths that scaffold will provide (relative to etc/<service>/)
        scaffold_provides = set()
        if scaffold_statics:
            service_scaffold = self.scaffold_dir / service
            for static in scaffold_statics:
                relative = static.relative_to(service_scaffold)
                # Convert to what the output path would be
                scaffold_provides.add(str(relative))

        # Find service YAML (check enabled first, then available)
        service_yml = self.services_enabled / f"{service}.yml"
        if not service_yml.exists():
            service_yml = self.services_available / f"{service}.yml"
            if not service_yml.exists():
                # No service YAML, nothing to do
                return True

        try:
            with open(service_yml, "r") as f:
                content = f.read()
        except Exception as e:
            print(f"  Error reading {service_yml}: {e}", file=sys.stderr)
            return False

        # Pattern to match ./etc/<service>/* volume mounts
        # Matches: ./etc/service/path or ./etc/service/file.ext
        pattern = rf"\./etc/{re.escape(service)}\S*"
        matches = re.findall(pattern, content)

        if not matches:
            return True

        print(f"  Creating etc/ volumes for {service}...")

        for match in matches:
            # Remove everything after : (the container path)
            volume_path = match.split(":")[0]

            # Convert to absolute path
            abs_path = self.base_dir / volume_path.lstrip("./")

            # Check if path relative to etc/<service>/ is provided by scaffold
            relative_to_service = str(abs_path).split(f"/etc/{service}/", 1)
            if len(relative_to_service) > 1:
                remainder = relative_to_service[1]

                # Skip if scaffold will provide this file
                if remainder in scaffold_provides:
                    print(f"    Skipping (scaffold provides): {remainder}")
                    continue

                # Check if the remainder contains a dot (file extension)
                if "." in Path(remainder).name:
                    # It's a file - create parent dir and touch file
                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    if not abs_path.exists():
                        abs_path.touch()
                        print(f"    Created file: {abs_path}")
                else:
                    # It's a directory
                    abs_path.mkdir(parents=True, exist_ok=True)
                    print(f"    Created dir: {abs_path}")
            else:
                # Just the service directory
                abs_path.mkdir(parents=True, exist_ok=True)
                print(f"    Created dir: {abs_path}")

        return True

    def _display_message(self, service: str) -> None:
        """Display post-enable message if MESSAGE.txt exists."""
        message_file = self.scaffold_dir / service / "MESSAGE.txt"
        if message_file.exists():
            print("\n" + "=" * 60)
            print(f"POST-ENABLE INSTRUCTIONS FOR {service.upper()}")
            print("=" * 60)
            print(message_file.read_text().strip())
            print("=" * 60 + "\n")

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

        # Create context (share executor with operations)
        ctx = OperationContext(
            service=service,
            base_dir=self.base_dir,
            scaffold_dir=self.scaffold_dir,
            etc_dir=self.etc_dir,
            services_enabled=self.services_enabled,
            command_executor=self._executor,
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
        print(f"Building scaffold for '{service}'...")
        success = True

        # Get scaffold files first (needed for volume creation check)
        templates, statics = self.find_scaffold_files(service)

        # Phase 0: Create etc/ volume directories from service YAML
        # Pass statics so it knows what scaffold will provide
        if not self.create_etc_volumes(service, statics):
            success = False

        # Check if we have scaffold files (may have none, just volume creation)
        if not templates and not statics and not self.find_manifest(service):
            print(f"  No scaffold templates for '{service}'")
            return success

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

        # Phase 4: Display post-enable message if exists
        if success:
            self._display_message(service)

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
