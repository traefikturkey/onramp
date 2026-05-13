#!/usr/bin/env python3
"""Test script to verify override parsing logic."""

import sys
from pathlib import Path

# Add the scripts directory to path
sys.path.insert(0, str(Path(__file__).parent / "sietch" / "scripts"))

from generate_service_docs import ServiceDocGenerator

def main():
    root_dir = Path(__file__).parent
    generator = ServiceDocGenerator(root_dir)

    # Test with audiobookshelf
    service_name = "audiobookshelf"
    print(f"Testing override detection for: {service_name}")
    print("=" * 60)

    overrides = generator.find_service_overrides(service_name)
    print(f"\nFound {len(overrides)} override(s):")
    for override_path in overrides:
        print(f"  - {override_path.name}")

    print("\nAnalyzing overrides:")
    print("-" * 60)

    for override_path in overrides:
        analysis = generator.analyze_override(override_path)
        print(f"\nOverride: {analysis['override_name']}")
        print(f"Purpose: {analysis['purpose']}")
        print(f"Volumes: {analysis['volumes']}")
        print(f"Services: {analysis['services']}")
        print(f"Env vars: {analysis['environment_vars']}")
        print(f"Comments: {analysis['comments']}")

    # Test format_override_section
    if overrides:
        print("\n\nFormatted override section:")
        print("=" * 60)
        analyses = [generator.analyze_override(p) for p in overrides]
        formatted = generator.format_override_section(analyses)
        print(formatted)

if __name__ == "__main__":
    main()
