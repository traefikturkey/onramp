#!/usr/bin/env python3
"""
Update SERVICES.md to link to the new documentation files.

Changes format from:
- [service](url) ([yml](yml-url)): description

To:
- [service](services-docs/service.md) | [yml](yml-url) | [upstream](upstream-url): description
"""

import re
from pathlib import Path


def update_services_md(root_dir: Path):
    """Update SERVICES.md with new format."""
    services_md_path = root_dir / "SERVICES.md"

    print("=" * 60)
    print("Updating SERVICES.md")
    print("=" * 60)
    print("")

    # Read the file
    with open(services_md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    updated_lines = []

    # Pattern to match service entries:
    # - [service](url) ([yml](yml-url)): description
    pattern = r'^- \[([^\]]+)\]\(([^)]+)\) \(\[yml\]\(([^)]+)\)\): (.+)$'

    for line in lines:
        match = re.match(pattern, line)

        if match:
            service_name = match.group(1)
            upstream_url = match.group(2)
            yml_url = match.group(3)
            description = match.group(4)

            # Convert service name to slug (lowercase, replace spaces with hyphens)
            service_slug = service_name.lower().replace(' ', '-')

            # Build new format
            new_line = f"- [{service_name}](services-docs/{service_slug}.md) | [yml]({yml_url}) | [upstream]({upstream_url}): {description}"
            updated_lines.append(new_line)
        else:
            # Keep line as-is if it doesn't match the pattern
            updated_lines.append(line)

    # Write back
    updated_content = '\n'.join(updated_lines)

    with open(services_md_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"Updated {services_md_path}")
    print("")
    print("New format:")
    print("- [service](services-docs/service.md) | [yml](yml-url) | [upstream](upstream-url): description")
    print("")
    print("Done!")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent

    update_services_md(root_dir)


if __name__ == "__main__":
    main()
