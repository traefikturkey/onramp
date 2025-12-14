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
import re
import secrets
import shutil
import string
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ports.command import CommandExecutor


def validate_path_within_base(path: Path, base: Path) -> bool:
    """Validate that a path stays within the base directory.

    Prevents path traversal attacks by checking that the resolved
    path is still under the base directory.

    Args:
        path: The path to validate
        base: The base directory that path must stay within

    Returns:
        True if path is safely within base, False otherwise
    """
    try:
        # Resolve both paths to absolute, following symlinks
        resolved_base = base.resolve()
        resolved_path = path.resolve()

        # Check if resolved path starts with resolved base
        # Using os.path.commonpath is more reliable than string comparison
        try:
            common = Path(os.path.commonpath([resolved_base, resolved_path]))
            return common == resolved_base
        except ValueError:
            # Different drives on Windows, or one path is relative
            return False
    except (OSError, RuntimeError):
        # Path doesn't exist or can't be resolved - be safe and reject
        return False

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

# Import postgres manager for database automation
try:
    from postgres_manager import PostgresManager

    POSTGRES_MANAGER_AVAILABLE = True
except ImportError:
    POSTGRES_MANAGER_AVAILABLE = False

# Import valkey manager for cache database automation
try:
    from valkey_manager import ValkeyManager

    VALKEY_MANAGER_AVAILABLE = True
except ImportError:
    VALKEY_MANAGER_AVAILABLE = False

# Import mariadb manager for database automation
try:
    from mariadb_manager import MariaDBManager

    MARIADB_MANAGER_AVAILABLE = True
except ImportError:
    MARIADB_MANAGER_AVAILABLE = False

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

        # Track created files/directories for rollback on failure
        self._created_files: list[Path] = []

        # Use injected executor or create default
        if executor is not None:
            self._executor = executor
        else:
            from adapters.subprocess_cmd import SubprocessCommandExecutor

            self._executor = SubprocessCommandExecutor()

    def _track_created(self, path: Path) -> None:
        """Track a created file or directory for potential rollback."""
        self._created_files.append(path)

    def _clear_tracking(self) -> None:
        """Clear the tracking list (after successful build)."""
        self._created_files.clear()

    def rollback(self) -> None:
        """Rollback created files and directories.

        Removes files and directories in reverse order of creation.
        Directories are only removed if empty.
        """
        # Process in reverse order (newest first)
        for path in reversed(self._created_files):
            try:
                if path.exists():
                    if path.is_file():
                        path.unlink()
                        print(f"  Rollback: removed file {path}")
                    elif path.is_dir():
                        # Only remove if empty
                        try:
                            path.rmdir()
                            print(f"  Rollback: removed directory {path}")
                        except OSError:
                            # Directory not empty, skip
                            pass
            except Exception as e:
                print(f"  Rollback warning: could not remove {path}: {e}", file=sys.stderr)

        self._created_files.clear()

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

    def _generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def _is_password_var(self, var_name: str) -> bool:
        """Check if a variable name looks like a password/secret."""
        password_patterns = (
            '_PASS', '_PASSWORD', '_SECRET', '_KEY', '_TOKEN',
            'PASS_', 'PASSWORD_', 'SECRET_', 'KEY_', 'TOKEN_',
        )
        upper_name = var_name.upper()
        return any(pattern in upper_name for pattern in password_patterns)

    def _render_template_string(self, content: str) -> str:
        """
        Render template content by substituting ${VAR} and ${VAR:-default} patterns.

        For password-like variables that are unset, generates secure random values.
        """
        # Pattern matches ${VAR} or ${VAR:-default} or ${VAR:?error}
        pattern = re.compile(r'\$\{([A-Z][A-Z0-9_]*)(?::-([^}]*)|:\?([^}]*))?\}')

        generated_passwords = {}

        def replace_var(match: re.Match) -> str:
            var_name = match.group(1)
            default_value = match.group(2)  # From ${VAR:-default}
            error_msg = match.group(3)  # From ${VAR:?error}

            # Check environment first
            env_value = os.environ.get(var_name)

            if env_value is not None and env_value != '':
                return env_value

            # If there's a default, use it
            if default_value is not None:
                return default_value

            # For password-like variables, generate a secure value
            if self._is_password_var(var_name):
                if var_name not in generated_passwords:
                    generated_passwords[var_name] = self._generate_secure_password()
                    print(f"    Generated secure value for {var_name}")
                return generated_passwords[var_name]

            # For error syntax ${VAR:?msg}, return empty (user must set it)
            if error_msg is not None:
                print(f"    Warning: {var_name} not set ({error_msg})")
                return ''

            # Variable not set and no default - return empty
            return ''

        return pattern.sub(replace_var, content)

    def render_template(self, source: Path, dest: Path, skip_if_exists: bool = True) -> bool:
        """Render a template file using Python string substitution.

        Args:
            source: Template file path
            dest: Output file path
            skip_if_exists: If True, don't overwrite existing files (default: True)
        """
        try:
            # Skip if destination exists (don't overwrite user configs)
            if skip_if_exists and dest.exists():
                print(f"  Skipped (exists): {dest}")
                return True

            dest.parent.mkdir(parents=True, exist_ok=True)
            with open(source, "r") as f:
                template_content = f.read()

            rendered_content = self._render_template_string(template_content)

            with open(dest, "w") as f:
                f.write(rendered_content)

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

        # The allowed base for this service's etc files
        allowed_base = self.etc_dir / service

        for match in matches:
            # Remove everything after : (the container path)
            volume_path = match.split(":")[0]

            # Convert to absolute path
            abs_path = self.base_dir / volume_path.lstrip("./")

            # SECURITY: Validate path stays within etc/<service>/
            # Resolve the path to handle any .. traversal attempts
            try:
                # For paths that don't exist yet, we need to check the normalized path
                # Use os.path.normpath to resolve .. without requiring the path to exist
                normalized = Path(os.path.normpath(abs_path))

                # Check it's under the etc directory
                if not str(normalized).startswith(str(self.etc_dir)):
                    print(f"    Skipping (path traversal attempt): {volume_path}")
                    continue

                # For existing paths, also check resolved path (handles symlinks)
                if abs_path.exists() and not validate_path_within_base(abs_path, self.etc_dir):
                    print(f"    Skipping (path escapes via symlink): {volume_path}")
                    continue
            except Exception as e:
                print(f"    Skipping (path validation error): {volume_path} - {e}")
                continue

            # Check if path relative to etc/<service>/ is provided by scaffold
            relative_to_service = str(abs_path).split(f"/etc/{service}/", 1)
            if len(relative_to_service) > 1:
                remainder = relative_to_service[1]

                # Skip if scaffold will provide this file
                if remainder in scaffold_provides:
                    print(f"    Skipping (scaffold provides): {remainder}")
                    continue

                # Determine if this is a file or directory
                is_directory = self._is_volume_directory(service, remainder, abs_path)

                if is_directory:
                    abs_path.mkdir(parents=True, exist_ok=True)
                    self._track_created(abs_path)
                    print(f"    Created dir: {abs_path}")
                else:
                    # It's a file - create parent dir and touch file
                    abs_path.parent.mkdir(parents=True, exist_ok=True)
                    if not abs_path.exists():
                        abs_path.touch()
                        self._track_created(abs_path)
                        print(f"    Created file: {abs_path}")
            else:
                # Just the service directory
                abs_path.mkdir(parents=True, exist_ok=True)
                self._track_created(abs_path)
                print(f"    Created dir: {abs_path}")

        return True

    def _is_volume_directory(self, service: str, remainder: str, abs_path: Path) -> bool:
        """Determine if a volume mount path should be a directory or file.

        Uses multiple heuristics since we can't always know from the path alone:
        1. If path already exists, use its actual type
        2. If scaffold has this path as a directory, it's a directory
        3. Check for file extension pattern (e.g., .conf, .yml, .json)
        4. Default to directory for ambiguous cases like 'hosts.d'
        """
        # If it already exists, use actual type
        if abs_path.exists():
            return abs_path.is_dir()

        # Check if scaffold source exists and is a directory
        scaffold_path = self.scaffold_dir / service / remainder
        if scaffold_path.exists():
            return scaffold_path.is_dir()

        # Check for common file extension patterns
        # A file extension is a dot followed by 1-4 alphanumeric characters at the end
        name = Path(remainder).name
        if "." in name:
            # Get the part after the last dot
            ext = name.rsplit(".", 1)[-1]
            # Common file extensions are 1-4 alphanumeric chars
            # Directories like "hosts.d", "conf.d" have .d which is just 1 char
            # but we should treat those as directories
            if ext.lower() in ("d", "daily", "weekly", "monthly", "available", "enabled"):
                return True  # These are directory naming conventions
            if len(ext) <= 4 and ext.isalnum():
                return False  # Likely a file extension

        # Default to directory for ambiguous cases
        return True

    def _parse_metadata(self, service: str) -> dict:
        """Parse metadata comments from service YAML file.

        Looks for metadata comments in the format:
        # key: value

        Supported metadata:
        - requires: svc1, svc2 (services that must be enabled/running first)
        - database: postgres (indicates service needs postgres)
        - database_name: dbname (name of database to create)
        - cache: valkey (indicates service needs valkey)
        - cache_db: N (optional: preferred valkey database number 0-15)

        Returns:
            Dictionary with metadata keys and values
        """
        metadata = {}

        # Check services-enabled first, then services-available
        service_yml = self.services_enabled / f"{service}.yml"
        if not service_yml.exists():
            service_yml = self.services_available / f"{service}.yml"
            if not service_yml.exists():
                return metadata

        try:
            with open(service_yml, "r") as f:
                for line in f:
                    line = line.strip()
                    # Look for metadata comments: # key: value
                    if line.startswith("# ") and ": " in line:
                        # Remove leading '# ' and split on first ':'
                        comment = line[2:].strip()
                        if comment.startswith("http"):
                            continue  # Skip URLs
                        if ": " in comment:
                            key, value = comment.split(": ", 1)
                            key = key.strip()
                            value = value.strip()
                            # Only store simple key-value metadata
                            if key in ("database", "database_name", "cache", "cache_db", "requires"):
                                metadata[key] = value
        except Exception as e:
            print(f"  Warning: Error parsing metadata from {service_yml}: {e}", file=sys.stderr)

        return metadata

    def _is_postgres_enabled(self) -> bool:
        """Check if postgres service is enabled."""
        postgres_yml = self.services_enabled / "postgres.yml"
        return postgres_yml.exists()

    def _is_valkey_enabled(self) -> bool:
        """Check if valkey service is enabled."""
        valkey_yml = self.services_enabled / "valkey.yml"
        return valkey_yml.exists()

    def _is_mariadb_enabled(self) -> bool:
        """Check if mariadb service is enabled."""
        mariadb_yml = self.services_enabled / "mariadb.yml"
        return mariadb_yml.exists()

    def _enable_dependency(self, service: str) -> bool:
        """Enable a dependency service (create symlink and run scaffold).

        Args:
            service: Service name to enable

        Returns:
            True if enabled successfully, False on error
        """
        service_yml = self.services_enabled / f"{service}.yml"
        available_yml = self.services_available / f"{service}.yml"

        # Check if already enabled
        if service_yml.exists():
            return True

        # Check if service exists in available
        if not available_yml.exists():
            print(f"  Error: Dependency '{service}' not found in services-available/", file=sys.stderr)
            return False

        print(f"  Auto-enabling dependency '{service}'...")

        # Create symlink
        try:
            service_yml.symlink_to(f"../services-available/{service}.yml")
            print(f"    Created symlink: {service}.yml -> ../services-available/{service}.yml")
        except Exception as e:
            print(f"  Error creating symlink for '{service}': {e}", file=sys.stderr)
            return False

        # Run scaffold for the dependency (but don't recurse infinitely)
        # Create a new scaffolder to avoid state issues
        dep_scaffolder = Scaffolder(str(self.base_dir), self._executor)
        if dep_scaffolder.has_scaffold(service):
            print(f"    Running scaffold for '{service}'...")
            if not dep_scaffolder.build(service):
                print(f"  Warning: Scaffold failed for '{service}', continuing anyway", file=sys.stderr)

        return True

    def _start_dependency(self, service: str, wait_seconds: int = 30) -> bool:
        """Start a dependency service and wait for it to be ready.

        Args:
            service: Service name to start
            wait_seconds: Seconds to wait for service to be ready

        Returns:
            True if started successfully, False on error
        """
        import time

        print(f"  Starting dependency '{service}'...")

        # Run docker compose up
        try:
            result = self._executor.run(
                [
                    "docker", "compose",
                    "--project-directory", str(self.base_dir),
                    "-f", f"services-enabled/{service}.yml",
                    "up", "-d", service
                ],
                capture_output=True,
                check=False,
            )

            if result.returncode != 0:
                print(f"  Error starting '{service}': {result.stderr}", file=sys.stderr)
                return False

            print(f"    Started '{service}', waiting for ready state...")
        except Exception as e:
            print(f"  Error starting '{service}': {e}", file=sys.stderr)
            return False

        # Wait for container to be running/healthy
        for i in range(wait_seconds):
            try:
                result = self._executor.run(
                    ["docker", "inspect", "-f", "{{.State.Status}}", service],
                    capture_output=True,
                    check=False,
                )
                status = result.stdout.strip() if result.stdout else ""

                if status == "running":
                    # Check for health status if available
                    health_result = self._executor.run(
                        ["docker", "inspect", "-f", "{{.State.Health.Status}}", service],
                        capture_output=True,
                        check=False,
                    )
                    health = health_result.stdout.strip() if health_result.stdout else ""

                    if health == "healthy" or health == "":
                        print(f"    '{service}' is ready")
                        return True
                    elif health == "starting":
                        pass  # Keep waiting
                    # For unhealthy, keep waiting a bit more

                time.sleep(1)
            except Exception:
                time.sleep(1)

        print(f"  Warning: '{service}' may not be fully ready after {wait_seconds}s", file=sys.stderr)
        return True  # Return True anyway to attempt database creation

    def _ensure_dependency(self, service: str, wait_seconds: int = 30) -> bool:
        """Ensure a dependency service is enabled and running.

        Args:
            service: Service name
            wait_seconds: Seconds to wait for service to be ready

        Returns:
            True if dependency is ready, False on error
        """
        # Enable if not already
        if not self._enable_dependency(service):
            return False

        # Check if running
        try:
            result = self._executor.run(
                ["docker", "inspect", "-f", "{{.State.Status}}", service],
                capture_output=True,
                check=False,
            )
            status = result.stdout.strip() if result.stdout else ""

            if status == "running":
                return True  # Already running
        except Exception:
            pass  # Not running, need to start

        # Start the service
        return self._start_dependency(service, wait_seconds)

    def _ensure_required_services(self, service: str, metadata: dict) -> bool:
        """Ensure all required services are enabled and running.

        Parses the 'requires' metadata which can be a comma-separated list
        of service names that must be enabled and running before this service.

        Args:
            service: Service name (for logging)
            metadata: Parsed metadata from service YAML

        Returns:
            True if all required services are ready, False on error
        """
        requires = metadata.get("requires", "")
        if not requires:
            return True

        # Parse comma-separated list of required services
        required_services = [s.strip() for s in requires.split(",") if s.strip()]
        if not required_services:
            return True

        for req_service in required_services:
            # Skip if it's the same service (avoid infinite loop)
            if req_service == service:
                continue

            # Check if required service exists
            req_yml = self.services_available / f"{req_service}.yml"
            if not req_yml.exists():
                print(f"  Warning: Required service '{req_service}' not found in services-available/", file=sys.stderr)
                continue

            # Ensure the required service is enabled and running
            if not self._ensure_dependency(req_service):
                print(f"  Error: Failed to enable/start required service '{req_service}'", file=sys.stderr)
                return False

        return True

    def _create_postgres_database(self, service: str, metadata: dict) -> bool:
        """Create PostgreSQL database if metadata indicates it's needed.

        Args:
            service: Service name
            metadata: Parsed metadata from service YAML

        Returns:
            True if database created successfully or not needed, False on error
        """
        # Check if service needs postgres
        if metadata.get("database") != "postgres":
            return True  # Not a postgres service, nothing to do

        # Check if database_name is specified
        database_name = metadata.get("database_name")
        if not database_name:
            print(f"  Warning: Service '{service}' uses postgres but no database_name specified", file=sys.stderr)
            return True  # Not a fatal error

        # Check if postgres manager is available
        if not POSTGRES_MANAGER_AVAILABLE:
            print(f"  Warning: postgres_manager not available, skipping database creation", file=sys.stderr)
            return True

        # Auto-enable and start postgres if needed
        if not self._ensure_dependency("postgres"):
            print(f"  Error: Failed to enable/start postgres dependency", file=sys.stderr)
            return False

        # Create database
        try:
            print(f"  Creating PostgreSQL database '{database_name}'...")
            pg_manager = PostgresManager()

            if pg_manager.database_exists(database_name):
                print(f"    Database '{database_name}' already exists")
                return True

            pg_manager.create_database(database_name)
            print(f"    Database '{database_name}' created successfully")
            return True
        except Exception as e:
            print(f"  Error creating database '{database_name}': {e}", file=sys.stderr)
            return False

    def _assign_valkey_database(self, service: str, metadata: dict) -> bool:
        """Assign Valkey database number if metadata indicates it's needed.

        Args:
            service: Service name
            metadata: Parsed metadata from service YAML

        Returns:
            True if database assigned successfully or not needed, False on error
        """
        # Check if service needs valkey
        if metadata.get("cache") != "valkey":
            return True  # Not a valkey service, nothing to do

        # Check if valkey manager is available
        if not VALKEY_MANAGER_AVAILABLE:
            print(f"  Warning: valkey_manager not available, skipping database assignment", file=sys.stderr)
            return True

        # Auto-enable and start valkey if needed
        if not self._ensure_dependency("valkey"):
            print(f"  Error: Failed to enable/start valkey dependency", file=sys.stderr)
            return False

        # Assign database number
        try:
            print(f"  Assigning Valkey database for '{service}'...")
            valkey_manager = ValkeyManager()

            # Check for preferred database number in metadata
            preferred_db = None
            if "cache_db" in metadata:
                try:
                    preferred_db = int(metadata["cache_db"])
                except ValueError:
                    print(f"  Warning: Invalid cache_db value '{metadata['cache_db']}', auto-assigning", file=sys.stderr)

            code, db_num = valkey_manager.assign_database(service, preferred_db)
            if code != 0:
                return False

            print(f"    Assigned DB {db_num} to '{service}'")
            return True
        except Exception as e:
            print(f"  Error assigning valkey database: {e}", file=sys.stderr)
            return False

    def _create_mariadb_database(self, service: str, metadata: dict) -> bool:
        """Create MariaDB database if metadata indicates it's needed.

        Args:
            service: Service name
            metadata: Parsed metadata from service YAML

        Returns:
            True if database created successfully or not needed, False on error
        """
        # Check if service needs mariadb
        if metadata.get("database") != "mariadb":
            return True  # Not a mariadb service, nothing to do

        # Check if database_name is specified
        database_name = metadata.get("database_name")
        if not database_name:
            print(f"  Warning: Service '{service}' uses mariadb but no database_name specified", file=sys.stderr)
            return True  # Not a fatal error

        # Check if mariadb manager is available
        if not MARIADB_MANAGER_AVAILABLE:
            print(f"  Warning: mariadb_manager not available, skipping database creation", file=sys.stderr)
            return True

        # Auto-enable and start mariadb if needed
        if not self._ensure_dependency("mariadb"):
            print(f"  Error: Failed to enable/start mariadb dependency", file=sys.stderr)
            return False

        # Create database
        try:
            print(f"  Creating MariaDB database '{database_name}'...")
            maria_manager = MariaDBManager()

            if maria_manager.database_exists(database_name):
                print(f"    Database '{database_name}' already exists")
                return True

            maria_manager.create_database(database_name)
            print(f"    Database '{database_name}' created successfully")
            return True
        except Exception as e:
            print(f"  Error creating mariadb database: {e}", file=sys.stderr)
            return False

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
        """Build scaffold for a service.

        On failure, performs rollback of created files/directories.
        """
        print(f"Building scaffold for '{service}'...")

        # Clear any previous tracking
        self._clear_tracking()

        success = True

        # Get scaffold files first (needed for volume creation check)
        templates, statics = self.find_scaffold_files(service)

        # Parse metadata from service YAML
        metadata = self._parse_metadata(service)

        # Phase -2: Ensure required services are enabled and running
        if not self._ensure_required_services(service, metadata):
            print(f"  Error: Failed to satisfy required services", file=sys.stderr)
            success = False

        # Phase -1: Create PostgreSQL database if needed (before volumes)
        if success and not self._create_postgres_database(service, metadata):
            success = False

        # Phase -1a: Create MariaDB database if needed (before volumes)
        if success and not self._create_mariadb_database(service, metadata):
            success = False

        # Phase -1b: Assign Valkey database if needed (before volumes)
        if success and not self._assign_valkey_database(service, metadata):
            success = False

        # Phase 0: Create etc/ volume directories from service YAML
        # Pass statics so it knows what scaffold will provide
        if success and not self.create_etc_volumes(service, statics):
            success = False

        # Check if we have scaffold files (may have none, just volume creation)
        if not templates and not statics and not self.find_manifest(service):
            print(f"  No scaffold templates for '{service}'")
            if success:
                self._clear_tracking()
            else:
                self.rollback()
            return success

        # Phase 1: Render templates
        if success:
            for template in templates:
                dest = self.get_output_path(service, template)
                if not self.render_template(template, dest):
                    success = False
                    break
                self._track_created(dest)

        # Phase 2: Copy static files
        if success:
            for static in statics:
                dest = self.get_output_path(service, static)
                if not self.copy_static(static, dest):
                    success = False
                    break
                self._track_created(dest)

        # Phase 3: Execute manifest operations (after templates/statics)
        if success and not self.execute_manifest(service):
            success = False

        # On failure, rollback created files
        if not success:
            print(f"  Build failed, rolling back changes...")
            self.rollback()
        else:
            # Success - clear tracking and display message
            self._clear_tracking()
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
