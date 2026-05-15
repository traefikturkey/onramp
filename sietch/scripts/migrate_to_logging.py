#!/usr/bin/env python
"""
Helper script to migrate print statements to logging framework.

This script provides utilities to help migrate the codebase from print()
statements to structured logging. It's meant to be run manually on files
that need migration.

Usage:
    python migrate_to_logging.py <file_path>
"""

import re
import sys
from pathlib import Path


def add_logging_import(content: str) -> str:
    """Add logging import after existing imports."""
    # Find the last import statement
    import_pattern = r"((?:^(?:import|from)\s+.+$\n?)+)"
    match = re.search(import_pattern, content, re.MULTILINE)

    if match:
        last_import_end = match.end()
        # Check if logging_config import already exists
        if "from logging_config import" in content:
            return content

        # Insert logging import
        imports = content[:last_import_end]
        rest = content[last_import_end:]

        # Add blank line and logging import
        new_imports = imports.rstrip() + "\n\nfrom logging_config import get_logger\n\nlogger = get_logger(__name__)\n"
        return new_imports + rest

    return content


def migrate_print_to_logging(content: str, filename: str) -> str:
    """
    Migrate print statements to logging calls.

    Rules:
    - print(f"Error: ...") -> logger.error(...)
    - print(f"Warning: ...") -> logger.warning(...)
    - print(f"    ...") (indented) -> logger.info(...) or logger.debug(...)
    - print(f"...") (normal) -> logger.info(...)
    """
    lines = content.split("\n")
    migrated_lines = []

    for line in lines:
        stripped = line.lstrip()
        indent = line[:len(line) - len(stripped)]

        # Skip if not a print statement
        if not stripped.startswith("print("):
            migrated_lines.append(line)
            continue

        # Extract the print content
        match = re.match(r'print\((.*)\)', stripped, re.DOTALL)
        if not match:
            migrated_lines.append(line)
            continue

        print_content = match.group(1).strip()

        # Determine log level
        lower_content = print_content.lower()
        if "error" in lower_content or "failed" in lower_content:
            level = "error"
        elif "warning" in lower_content or "warn" in lower_content:
            level = "warning"
        elif stripped.startswith("print(f\"    ") or stripped.startswith('print(f"    '):
            # Indented messages are usually debug/info
            if "skipped" in lower_content or "exists" in lower_content:
                level = "debug"
            else:
                level = "info"
        else:
            level = "info"

        # Convert the message
        # Handle f-strings
        if print_content.startswith('f"') or print_content.startswith("f'"):
            # Extract the f-string content
            quote_char = print_content[1]
            msg_match = re.match(rf'f{quote_char}(.+){quote_char}', print_content)
            if msg_match:
                msg_content = msg_match.group(1)

                # Find variables in the f-string
                var_pattern = r'\{([^}]+)\}'
                variables = re.findall(var_pattern, msg_content)

                # Remove the "    " prefix from indented messages
                msg_content = re.sub(r'^    ', '', msg_content)

                # Remove variables from message
                clean_msg = re.sub(var_pattern, '', msg_content).strip()
                clean_msg = clean_msg.replace(":", "").strip()

                # Build extra dict if we have variables
                if variables:
                    extra_items = []
                    for var in variables:
                        # Simple variable name extraction
                        var_name = var.split(".")[-1].split("[")[0]
                        extra_items.append(f'"{var_name}": {var}')

                    extra_dict = ", extra={" + ", ".join(extra_items) + "}"
                else:
                    extra_dict = ""

                migrated_line = f'{indent}logger.{level}("{clean_msg}"{extra_dict})'
            else:
                # Fallback
                migrated_line = f'{indent}logger.{level}({print_content})'
        else:
            # Regular string
            migrated_line = f'{indent}logger.{level}({print_content})'

        migrated_lines.append(migrated_line)

    return "\n".join(migrated_lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python migrate_to_logging.py <file_path>")
        sys.exit(1)

    file_path = Path(sys.argv[1])

    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)

    # Read file
    content = file_path.read_text(encoding="utf-8")

    # Add logging import
    content = add_logging_import(content)

    # Migrate print statements
    content = migrate_print_to_logging(content, file_path.name)

    # Write back
    backup_path = file_path.with_suffix(file_path.suffix + ".backup")
    file_path.rename(backup_path)
    print(f"Created backup: {backup_path}")

    file_path.write_text(content, encoding="utf-8")
    print(f"Migrated: {file_path}")
    print("\nPlease review the changes and adjust log levels/messages as needed.")


if __name__ == "__main__":
    main()
