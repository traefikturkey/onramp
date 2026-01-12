#!/usr/bin/env python
"""
env_wizard.py - Interactive environment setup wizard for OnRamp

Prompts users for required environment variables with helpful context,
replacing the manual editor-based setup flow.

Usage:
    python env_wizard.py                Run the wizard
    python env_wizard.py --skip-wizard  Skip interactive prompts (for automation)
    python env_wizard.py --check        Check if configuration is complete
"""

import argparse
import getpass
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class EnvVariable:
    """Metadata for an environment variable."""

    name: str
    help_text: str
    sensitive: bool = False
    required: bool = True
    default: str | None = None
    choices: list[tuple[str, str]] | None = None  # [(value, label), ...]


# Common timezone choices for the picker
COMMON_TIMEZONES = [
    ("US/Eastern", "US Eastern (New York)"),
    ("US/Central", "US Central (Chicago)"),
    ("US/Mountain", "US Mountain (Denver)"),
    ("US/Pacific", "US Pacific (Los Angeles)"),
    ("Europe/London", "Europe/London (GMT/BST)"),
    ("Europe/Paris", "Europe/Paris (CET/CEST)"),
    ("Europe/Berlin", "Europe/Berlin (CET/CEST)"),
    ("Europe/Amsterdam", "Europe/Amsterdam (CET/CEST)"),
]

# Main .env variables (required)
MAIN_ENV_VARS = [
    EnvVariable(
        name="HOST_NAME",
        help_text="Server hostname (will be used in service URLs)\nExample: myserver",
    ),
    EnvVariable(
        name="HOST_DOMAIN",
        help_text="Your domain name for SSL certificates and service URLs\nExample: example.com",
    ),
    EnvVariable(
        name="TZ",
        help_text="Timezone for containers",
        choices=COMMON_TIMEZONES,
    ),
    EnvVariable(
        name="CF_API_EMAIL",
        help_text="Email address for your Cloudflare account",
    ),
    EnvVariable(
        name="CF_DNS_API_TOKEN",
        help_text="""Cloudflare API token for DNS-01 SSL certificate challenges

Create one at: https://dash.cloudflare.com/profile/api-tokens
  1. Click "Create Token"
  2. Use "Edit zone DNS" template
  3. Zone Resources: Include -> Specific zone -> your domain
  4. Copy the generated token""",
        sensitive=True,
    ),
]

# NFS variables (conditional)
NFS_ENV_VARS = [
    EnvVariable(
        name="NFS_SERVER",
        help_text="IP address or hostname of your NFS server\nExample: 192.168.1.100 or nas.local",
    ),
]


class EnvWizard:
    """Interactive wizard for OnRamp environment setup."""

    def __init__(self, base_dir: str = "/app"):
        self.base_dir = Path(base_dir)
        self.services_enabled = self.base_dir / "services-enabled"
        self.main_env_file = self.services_enabled / ".env"
        self.nfs_env_file = self.services_enabled / ".env.nfs"

    def get_system_timezone(self) -> str | None:
        """Detect the current system timezone."""
        # Try /etc/timezone (Debian/Ubuntu)
        tz_file = Path("/etc/timezone")
        if tz_file.exists():
            tz = tz_file.read_text().strip()
            if tz and tz != "Etc/UTC" and tz != "UTC":
                return tz

        # Try /etc/localtime symlink (most distros)
        localtime = Path("/etc/localtime")
        if localtime.is_symlink():
            target = os.readlink(localtime)
            # Extract timezone from path like /usr/share/zoneinfo/America/New_York
            if "zoneinfo/" in target:
                tz = target.split("zoneinfo/")[-1]
                if tz and tz != "Etc/UTC" and tz != "UTC":
                    return tz

        # Try TZ environment variable
        tz = os.environ.get("TZ")
        if tz and tz != "Etc/UTC" and tz != "UTC":
            return tz

        return None

    def load_env_file(self, path: Path) -> dict[str, str]:
        """Load an env file and return a dict of var_name -> value."""
        variables: dict[str, str] = {}
        if not path.exists():
            return variables

        with open(path, "r") as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse KEY=value
                match = re.match(r"^([A-Z][A-Z0-9_]*)=(.*)$", line)
                if match:
                    var_name, value = match.groups()
                    variables[var_name] = value

        return variables

    def get_existing_value(self, var_name: str, env_vars: dict[str, str]) -> str | None:
        """Get an existing value for a variable, returns None if empty or missing."""
        value = env_vars.get(var_name, "")
        # Treat empty, placeholder, or template values as not set
        if not value or value.startswith("<") or value.startswith("${"):
            return None
        return value

    def update_env_file(self, path: Path, updates: dict[str, str]) -> None:
        """
        Update an env file with new values, preserving existing structure.

        If a variable exists, update its value. If not, append to end.
        """
        if not updates:
            return

        path.parent.mkdir(parents=True, exist_ok=True)

        # Read existing content
        lines: list[str] = []
        if path.exists():
            with open(path, "r") as f:
                lines = f.readlines()

        # Track which variables we've updated
        updated: set[str] = set()

        # Update existing lines
        new_lines: list[str] = []
        for line in lines:
            stripped = line.rstrip("\n\r")
            match = re.match(r"^([A-Z][A-Z0-9_]*)=", stripped)
            if match:
                var_name = match.group(1)
                if var_name in updates:
                    new_lines.append(f"{var_name}={updates[var_name]}\n")
                    updated.add(var_name)
                else:
                    new_lines.append(line if line.endswith("\n") else line + "\n")
            else:
                new_lines.append(line if line.endswith("\n") else line + "\n")

        # Append any new variables that weren't in the file
        for var_name, value in updates.items():
            if var_name not in updated:
                new_lines.append(f"{var_name}={value}\n")

        # Write back
        with open(path, "w") as f:
            f.writelines(new_lines)

    def prompt_text(self, var: EnvVariable, default: str | None = None) -> str:
        """Prompt for a text value with help text."""
        print(f"\n{var.name}")
        print("-" * len(var.name))
        print(var.help_text)

        if default:
            prompt = f"> [{default}]: "
        else:
            prompt = "> "

        while True:
            try:
                value = input(prompt).strip()
                if not value and default:
                    return default
                if value:
                    return value
                if not var.required:
                    return ""
                print("This field is required. Please enter a value.")
            except EOFError:
                # Non-interactive, use default if available
                if default:
                    return default
                return ""

    def prompt_sensitive(self, var: EnvVariable) -> str:
        """Prompt for a sensitive value (hidden input)."""
        print(f"\n{var.name}")
        print("-" * len(var.name))
        print(var.help_text)

        while True:
            try:
                value = getpass.getpass("> ")
                if value:
                    return value
                if not var.required:
                    return ""
                print("This field is required. Please enter a value.")
            except EOFError:
                return ""

    def prompt_choice(self, var: EnvVariable, choices: list[tuple[str, str]]) -> str:
        """Prompt with a numbered menu of choices."""
        print(f"\n{var.name}")
        print("-" * len(var.name))
        print(var.help_text)
        print()

        for i, (value, label) in enumerate(choices, 1):
            print(f"  {i}. {label}")
        print(f"  {len(choices) + 1}. Other (enter manually)")

        while True:
            try:
                choice = input("> ").strip()

                # Check for direct number input
                if choice.isdigit():
                    idx = int(choice)
                    if 1 <= idx <= len(choices):
                        return choices[idx - 1][0]
                    elif idx == len(choices) + 1:
                        # Other - manual entry
                        return input("Enter value: ").strip()

                # Allow typing the value directly
                if choice:
                    # Check if it matches a choice value
                    for value, _ in choices:
                        if choice.lower() == value.lower():
                            return value
                    # Accept as manual entry
                    return choice

                if not var.required:
                    return ""
                print("Please select an option or enter a value.")
            except EOFError:
                return ""

    def prompt_timezone(self) -> str:
        """
        Prompt for timezone, using system timezone if not UTC.

        Returns the selected timezone string.
        """
        system_tz = self.get_system_timezone()

        if system_tz:
            # System has a non-UTC timezone, offer it as default
            print(f"\nTZ")
            print("-" * 2)
            print(f"Detected system timezone: {system_tz}")
            print()
            try:
                use_system = input(f"Use {system_tz}? [Y/n]: ").strip().lower()
                if use_system in ("", "y", "yes"):
                    return system_tz
            except EOFError:
                return system_tz

        # Show timezone picker
        tz_var = EnvVariable(
            name="TZ",
            help_text="Select your timezone:",
            choices=COMMON_TIMEZONES,
        )
        return self.prompt_choice(tz_var, COMMON_TIMEZONES)

    def prompt_yes_no(self, question: str, default: bool = False) -> bool:
        """Prompt for a yes/no answer."""
        suffix = "[y/N]" if not default else "[Y/n]"
        try:
            answer = input(f"\n{question} {suffix}: ").strip().lower()
            if not answer:
                return default
            return answer in ("y", "yes")
        except EOFError:
            return default

    def prompt_variable(self, var: EnvVariable, existing_value: str | None = None) -> str | None:
        """
        Prompt for a single variable, handling different input types.

        Returns None if user wants to skip, otherwise returns the value.
        """
        # Skip if already set
        if existing_value:
            return None

        # Handle timezone specially
        if var.name == "TZ":
            return self.prompt_timezone()

        # Handle sensitive input
        if var.sensitive:
            return self.prompt_sensitive(var)

        # Handle choice input
        if var.choices:
            return self.prompt_choice(var, var.choices)

        # Default text input
        return self.prompt_text(var, var.default)

    def check_complete(self) -> tuple[bool, list[str]]:
        """
        Check if all required variables are configured.

        Returns (is_complete, list of missing variable names).
        """
        main_env = self.load_env_file(self.main_env_file)
        missing: list[str] = []

        for var in MAIN_ENV_VARS:
            if var.required and not self.get_existing_value(var.name, main_env):
                missing.append(var.name)

        return len(missing) == 0, missing

    def run_wizard(self, skip_wizard: bool = False) -> bool:
        """
        Run the interactive setup wizard.

        Returns True if configuration is complete, False otherwise.
        """
        print("=" * 50)
        print("OnRamp Environment Setup Wizard")
        print("=" * 50)

        # Load existing values
        main_env = self.load_env_file(self.main_env_file)
        nfs_env = self.load_env_file(self.nfs_env_file)

        # Check what's already configured
        is_complete, missing = self.check_complete()
        if is_complete:
            print("\nAll required values are already configured.")
            return True

        if skip_wizard:
            print("\nSkipping wizard (--skip-wizard flag).")
            print(f"Missing required values: {', '.join(missing)}")
            print("Run 'make edit-env-onramp' to configure manually.")
            return False

        # Offer escape hatch
        print(f"\nMissing configuration: {', '.join(missing)}")
        if not self.prompt_yes_no("Would you like to configure these now?", default=True):
            print("\nSkipping wizard. Run 'make edit-env-onramp' to configure manually.")
            return False

        # Collect new values
        main_updates: dict[str, str] = {}
        nfs_updates: dict[str, str] = {}

        # Auto-detect PUID/PGID
        puid = os.environ.get("PUID") or str(os.getuid())
        pgid = os.environ.get("PGID") or str(os.getgid())

        if not self.get_existing_value("PUID", main_env):
            main_updates["PUID"] = puid
            print(f"\nAuto-detected PUID: {puid}")

        if not self.get_existing_value("PGID", main_env):
            main_updates["PGID"] = pgid
            print(f"Auto-detected PGID: {pgid}")

        # Prompt for main env vars
        for var in MAIN_ENV_VARS:
            existing = self.get_existing_value(var.name, main_env)
            value = self.prompt_variable(var, existing)
            if value is not None:
                main_updates[var.name] = value

        # Ask about NFS
        if self.prompt_yes_no("Do you plan to use NFS for media files?", default=False):
            for var in NFS_ENV_VARS:
                existing = self.get_existing_value(var.name, nfs_env)
                value = self.prompt_variable(var, existing)
                if value is not None:
                    nfs_updates[var.name] = value

        # Write updates
        if main_updates:
            self.update_env_file(self.main_env_file, main_updates)
            print(f"\nUpdated: {self.main_env_file}")

        if nfs_updates:
            self.update_env_file(self.nfs_env_file, nfs_updates)
            print(f"Updated: {self.nfs_env_file}")

        print("\n" + "=" * 50)
        print("Configuration complete!")
        print("=" * 50)

        return True


def main():
    parser = argparse.ArgumentParser(
        description="Interactive environment setup wizard for OnRamp",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--skip-wizard",
        action="store_true",
        help="Skip interactive prompts (for automation)",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if configuration is complete without prompting",
    )
    parser.add_argument(
        "--base-dir",
        default="/app",
        help="Base directory (default: /app)",
    )

    args = parser.parse_args()

    wizard = EnvWizard(args.base_dir)

    if args.check:
        is_complete, missing = wizard.check_complete()
        if is_complete:
            print("Configuration is complete.")
            return 0
        else:
            print(f"Missing required values: {', '.join(missing)}")
            return 1

    success = wizard.run_wizard(skip_wizard=args.skip_wizard)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
