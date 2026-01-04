#!/usr/bin/env python
"""
traefik_hosts.py - Extract Traefik external Host() rules for Joyride DNS

Parses external-enabled/*.yml files, extracts Host() rules, resolves environment
variables, and generates a hosts file for Joyride DNS ingestion.

Commands:
  sync    Parse externals and update Joyride hosts file

Features:
- Early exit if Joyride service is not enabled
- Excludes middleware-only YAML files
- Resolves {{env "VAR"}} Go template syntax
- FQDN-based deduplication (new entries override existing)
- Preserves existing host entries and comments
"""

import argparse
import os
import re
import sys
from pathlib import Path


# Files that only define middlewares, not routers with Host() rules
MIDDLEWARE_ONLY_FILES = frozenset({
    "middleware.yml",
    "authentik_middleware.yml",
    "authelia_middlewares.yml",
    "crowdsec-bouncer.yml",
})

# Regex to extract Host() rules from Traefik dynamic config
# Matches: Host(`{{env "VAR"}}.{{env "HOST_DOMAIN"}}`) or Host(`hostname.domain`)
HOST_RULE_PATTERN = re.compile(r'rule:\s*"Host\(`([^`]+)`\)"')

# Regex to extract {{env "VAR"}} Go template syntax
ENV_TEMPLATE_PATTERN = re.compile(r'\{\{env\s+"([^"]+)"\}\}')


class TraefikHostsExtractor:
    """Extract Host() rules from Traefik external configs for Joyride DNS."""

    def __init__(
        self,
        base_dir: Path | None = None,
        env_vars: dict[str, str] | None = None,
    ):
        """Initialize extractor.

        Args:
            base_dir: Repository root directory (default: /app for container context)
            env_vars: Environment variables for template resolution (default: os.environ)
        """
        self.base_dir = base_dir or Path("/app")
        self.env_vars = env_vars if env_vars is not None else dict(os.environ)

        # Paths
        self.services_enabled = self.base_dir / "services-enabled"
        self.external_enabled = self.base_dir / "external-enabled"
        self.hosts_file = self.base_dir / "etc" / "joyride" / "hosts.d" / "hosts"

    def check_joyride_enabled(self) -> bool:
        """Check if Joyride service is enabled.

        Returns:
            True if joyride.yml exists in services-enabled
        """
        joyride_yml = self.services_enabled / "joyride.yml"
        return joyride_yml.exists()

    def load_env_files(self) -> None:
        """Load environment variables from .env and .env.external files."""
        env_file = self.services_enabled / ".env"
        env_external = self.services_enabled / ".env.external"

        for env_path in [env_file, env_external]:
            if env_path.exists():
                self._parse_env_file(env_path)

    def _parse_env_file(self, path: Path) -> None:
        """Parse a .env file and add to env_vars.

        Args:
            path: Path to .env file
        """
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=VALUE
                if "=" in line:
                    key, _, value = line.partition("=")
                    key = key.strip()
                    value = value.strip()
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    # Don't override existing env vars (allows CLI override)
                    if key not in self.env_vars:
                        self.env_vars[key] = value

    def resolve_template(self, template: str) -> str | None:
        """Resolve {{env "VAR"}} templates in a string.

        Args:
            template: String containing {{env "VAR"}} patterns

        Returns:
            Resolved string, or None if any required variable is empty/missing
        """
        result = template

        for match in ENV_TEMPLATE_PATTERN.finditer(template):
            var_name = match.group(1)
            var_value = self.env_vars.get(var_name, "")

            if not var_value:
                return None

            result = result.replace(match.group(0), var_value)

        return result

    def extract_hosts_from_file(self, yaml_path: Path) -> list[tuple[str, str]]:
        """Extract Host() rules from a Traefik external config file.

        Args:
            yaml_path: Path to YAML file

        Returns:
            List of (fqdn, source_file) tuples
        """
        hosts: list[tuple[str, str]] = []
        source_name = yaml_path.stem  # e.g., "homeassistant" from "homeassistant.yml"

        try:
            content = yaml_path.read_text(encoding="utf-8")
        except OSError as e:
            print(f"Warning: Could not read {yaml_path}: {e}", file=sys.stderr)
            return hosts

        for match in HOST_RULE_PATTERN.finditer(content):
            host_template = match.group(1)
            resolved = self.resolve_template(host_template)

            if resolved:
                hosts.append((resolved, source_name))
            else:
                # Identify which variable is missing
                missing_vars = []
                for env_match in ENV_TEMPLATE_PATTERN.finditer(host_template):
                    var_name = env_match.group(1)
                    if not self.env_vars.get(var_name):
                        missing_vars.append(var_name)

                if missing_vars:
                    print(
                        f"Skipped {source_name}: {', '.join(missing_vars)} not set",
                        file=sys.stderr,
                    )

        return hosts

    def get_external_files(self) -> list[Path]:
        """Get list of external config files to process.

        Returns:
            List of YAML file paths, excluding middleware-only files
        """
        if not self.external_enabled.exists():
            return []

        files = []
        for path in self.external_enabled.glob("*.yml"):
            if path.name not in MIDDLEWARE_ONLY_FILES:
                files.append(path)

        return sorted(files)

    def read_existing_hosts(self) -> tuple[list[str], dict[str, str]]:
        """Read existing hosts file content.

        Returns:
            Tuple of (comment_lines, fqdn_to_line_mapping)
        """
        comments: list[str] = []
        entries: dict[str, str] = {}  # fqdn -> full line

        if not self.hosts_file.exists():
            return comments, entries

        try:
            content = self.hosts_file.read_text(encoding="utf-8")
        except OSError:
            return comments, entries

        for line in content.splitlines():
            stripped = line.strip()

            if not stripped:
                continue
            elif stripped.startswith("#"):
                comments.append(line)
            else:
                # Parse "IP FQDN [aliases...]" format
                parts = stripped.split()
                if len(parts) >= 2:
                    fqdn = parts[1]
                    entries[fqdn] = line

        return comments, entries

    def write_hosts_file(
        self,
        comments: list[str],
        entries: dict[str, str],
    ) -> int:
        """Write hosts file with updated entries.

        Args:
            comments: Comment lines to preserve
            entries: FQDN -> line mapping

        Returns:
            Number of entries written
        """
        # Ensure directory exists
        self.hosts_file.parent.mkdir(parents=True, exist_ok=True)

        lines = []

        # Add preserved comments first
        lines.extend(comments)

        # Add blank line after comments if there are comments
        if comments:
            lines.append("")

        # Add entries sorted by FQDN
        for fqdn in sorted(entries.keys()):
            lines.append(entries[fqdn])

        # Write file
        self.hosts_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

        return len(entries)

    def sync(self) -> int:
        """Main sync operation.

        Returns:
            Exit code (0 = success, 1 = error)
        """
        # Early exit if joyride not enabled
        if not self.check_joyride_enabled():
            print(
                "Joyride service is not enabled. "
                "Enable it with: make enable-service NAME=joyride",
                file=sys.stderr,
            )
            return 1

        # Load environment variables
        self.load_env_files()

        # Check required vars
        hostip = self.env_vars.get("HOSTIP", "")
        host_domain = self.env_vars.get("HOST_DOMAIN", "")

        if not hostip:
            print("Error: HOSTIP not set in environment", file=sys.stderr)
            return 1

        if not host_domain:
            print("Error: HOST_DOMAIN not set in environment", file=sys.stderr)
            return 1

        # Get external files to process
        external_files = self.get_external_files()

        if not external_files:
            print("No external configs found in external-enabled/")
            return 0

        # Read existing hosts file
        comments, entries = self.read_existing_hosts()

        # Extract hosts from each file
        added: list[str] = []
        updated: list[str] = []

        for yaml_path in external_files:
            hosts = self.extract_hosts_from_file(yaml_path)

            for fqdn, source in hosts:
                new_line = f"{hostip} {fqdn}"

                if fqdn in entries:
                    if entries[fqdn] != new_line:
                        updated.append(fqdn)
                else:
                    added.append(fqdn)

                entries[fqdn] = new_line

        # Write updated hosts file
        total = self.write_hosts_file(comments, entries)

        # Print summary
        if added:
            print(f"Added: {', '.join(added)}")
        if updated:
            print(f"Updated: {', '.join(updated)}")

        print(f"Wrote {total} host entries to {self.hosts_file}")

        return 0


def main() -> int:
    """Command-line entry point."""
    parser = argparse.ArgumentParser(
        description="Extract Traefik external Host() rules for Joyride DNS",
    )
    parser.add_argument(
        "command",
        choices=["sync"],
        help="Command to run",
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=None,
        help="Repository root directory (default: /app)",
    )

    args = parser.parse_args()

    extractor = TraefikHostsExtractor(base_dir=args.base_dir)

    if args.command == "sync":
        return extractor.sync()

    return 0


if __name__ == "__main__":
    sys.exit(main())
