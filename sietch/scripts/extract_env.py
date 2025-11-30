#!/usr/bin/env python
"""
extract_env.py - Extract environment variables from Docker Compose files

Scans a service's compose YAML file and extracts environment variables,
generating an env.template file for the service's scaffold directory.

Features:
- Extracts variables from environment, volumes, labels, and image sections
- Groups variables by purpose (Docker, Container, Paths, Feature flags, etc.)
- Preserves default values from ${VAR:-default} patterns
- Generates formatted env.template with header and comments

Usage:
    python extract_env.py <service_name>
    python extract_env.py <service_name> --dry-run
"""

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractedVar:
    """Represents an extracted environment variable."""

    name: str
    default: str | None = None
    source: str = ""  # Where it was found (environment, volumes, labels, etc.)


@dataclass
class EnvExtractor:
    """Extracts environment variables from Docker Compose files."""

    base_dir: Path = field(default_factory=lambda: Path("/app"))

    def __post_init__(self) -> None:
        self.services_available = self.base_dir / "services-available"
        self.scaffold_dir = self.base_dir / "services-scaffold"

    def find_compose_file(self, service: str) -> Path | None:
        """Find the compose file for a service."""
        # Check main services-available
        compose_file = self.services_available / f"{service}.yml"
        if compose_file.exists():
            return compose_file

        # Check games subdirectory
        compose_file = self.services_available / "games" / f"{service}.yml"
        if compose_file.exists():
            return compose_file

        return None

    def extract_variables(self, content: str, service: str) -> dict[str, ExtractedVar]:
        """Extract all environment variables from compose file content."""
        variables: dict[str, ExtractedVar] = {}
        service_upper = service.upper().replace("-", "_")

        # Pattern to match ${VAR} or ${VAR:-default} or ${VAR:=default}
        # Handles nested ${...} in default values by matching balanced braces
        var_pattern = re.compile(
            r"\$\{([A-Z_][A-Z0-9_]*)(?::-|:=)?((?:[^{}]|\$\{[^}]*\})*)\}"
        )

        for match in var_pattern.finditer(content):
            var_name = match.group(1)
            default_value = match.group(2) if match.group(2) else None

            # Skip global/common variables that shouldn't be in service env
            if var_name in ("PUID", "PGID", "TZ", "HOST_DOMAIN", "HOST_NAME"):
                continue

            # Only include variables that start with the service prefix
            # or are clearly service-specific
            if var_name.startswith(service_upper):
                if var_name not in variables:
                    variables[var_name] = ExtractedVar(
                        name=var_name,
                        default=default_value,
                        source=self._determine_source(var_name),
                    )

        return variables

    def _determine_source(self, var_name: str) -> str:
        """Determine the category/source of a variable based on its name."""
        name_lower = var_name.lower()

        if "docker_tag" in name_lower:
            return "docker"
        elif "container_name" in name_lower:
            return "container"
        elif "restart" in name_lower:
            return "container"
        elif "host_name" in name_lower:
            return "network"
        elif "port" in name_lower:
            return "network"
        elif "path" in name_lower or "dir" in name_lower or "media" in name_lower:
            return "paths"
        elif "enabled" in name_lower:
            return "features"
        elif (
            "password" in name_lower
            or "secret" in name_lower
            or "token" in name_lower
            or "key" in name_lower
        ):
            return "secrets"
        elif "url" in name_lower or "instance" in name_lower:
            return "connection"
        elif "label" in name_lower:
            return "runner"
        else:
            return "config"

    def generate_env_template(
        self, service: str, variables: dict[str, ExtractedVar]
    ) -> str:
        """Generate env.template content from extracted variables."""
        service_upper = service.upper().replace("-", "_")
        service_title = service.replace("-", " ").title()

        lines = [
            "###############################################",
            f"# {service_title} Configuration",
            "#",
            f"# Generated from services-scaffold/{service}/env.template",
            f"# To regenerate: make scaffold-build {service}",
            "###############################################",
            "",
        ]

        # Group variables by source
        groups: dict[str, list[ExtractedVar]] = {}
        for var in variables.values():
            source = var.source
            if source not in groups:
                groups[source] = []
            groups[source].append(var)

        # Define group order and titles
        group_order = [
            ("docker", "Docker image settings"),
            ("container", "Container settings"),
            ("connection", "Connection settings"),
            ("network", "Network settings"),
            ("paths", "Path settings"),
            ("secrets", "Secrets and credentials"),
            ("runner", "Runner settings"),
            ("features", "Feature flags"),
            ("config", "Configuration"),
        ]

        for group_key, group_title in group_order:
            if group_key in groups:
                lines.append(f"# {group_title}")
                for var in sorted(groups[group_key], key=lambda v: v.name):
                    if var.default is not None and var.default != "":
                        lines.append(f"{var.name}=${{{var.name}:-{var.default}}}")
                    else:
                        lines.append(f"{var.name}=${{{var.name}}}")
                lines.append("")

        return "\n".join(lines)

    def create_scaffold_env(
        self, service: str, dry_run: bool = False
    ) -> tuple[bool, str]:
        """Create env.template for a service from its compose file."""
        compose_file = self.find_compose_file(service)
        if not compose_file:
            return False, f"Compose file not found for service: {service}"

        content = compose_file.read_text()
        variables = self.extract_variables(content, service)

        if not variables:
            return False, f"No service-specific variables found in {compose_file}"

        env_content = self.generate_env_template(service, variables)

        if dry_run:
            return True, env_content

        # Create scaffold directory if needed
        scaffold_service_dir = self.scaffold_dir / service
        scaffold_service_dir.mkdir(parents=True, exist_ok=True)

        # Write env.template
        env_template_path = scaffold_service_dir / "env.template"
        env_template_path.write_text(env_content)

        return True, f"Created {env_template_path}"


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Extract environment variables from compose file to env.template"
    )
    parser.add_argument("service", help="Service name")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing",
    )
    parser.add_argument(
        "--base-dir",
        default="/app",
        help="Base directory (default: /app)",
    )

    args = parser.parse_args()

    extractor = EnvExtractor(base_dir=Path(args.base_dir))
    success, result = extractor.create_scaffold_env(args.service, dry_run=args.dry_run)

    if success:
        print(result)
        return 0
    else:
        print(f"Error: {result}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
