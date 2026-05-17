#!/usr/bin/env python
"""
healthcheck_audit.py - Audit services for health check configuration

Scans service YAML files to identify:
- Services with autoheal=true but no healthcheck
- Services lacking health checks entirely
- Health check coverage statistics

Usage:
  healthcheck_audit.py [--enabled-only] [--format=text|json]
"""

from logging_config import get_logger, setup_logging
logger = get_logger(__name__)

import argparse
import json
import re
import sys
from pathlib import Path


def parse_service_yaml(filepath: Path) -> dict:
    """Parse service YAML to extract health check and autoheal info.

    Uses simple regex parsing to avoid yaml dependency for basic analysis.
    """
    content = filepath.read_text()

    result = {
        "file": filepath.name,
        "service": filepath.stem,
        "has_healthcheck": False,
        "has_autoheal": False,
        "autoheal_value": None,
        "services": [],
    }

    # Check for healthcheck block
    if re.search(r"healthcheck:", content):
        result["has_healthcheck"] = True

    # Check for autoheal label
    autoheal_match = re.search(r"autoheal[=:](\S+)", content)
    if autoheal_match:
        result["has_autoheal"] = True
        result["autoheal_value"] = autoheal_match.group(1).strip("\"'")

    # Extract service names (basic parsing)
    services_match = re.search(r"services:\s*\n((?:\s+\S+:.*\n?)+)", content)
    if services_match:
        service_lines = services_match.group(1)
        for match in re.finditer(r"^\s{2}(\w[\w-]*):", service_lines, re.MULTILINE):
            result["services"].append(match.group(1))

    return result


def audit_services(
    base_dir: Path, enabled_only: bool = False
) -> tuple[list[dict], dict]:
    """Audit all services for health check configuration.

    Returns:
        Tuple of (service_results, statistics)
    """
    services_available = base_dir / "services-available"
    services_enabled = base_dir / "services-enabled"

    results = []
    stats = {
        "total": 0,
        "with_healthcheck": 0,
        "with_autoheal": 0,
        "autoheal_no_healthcheck": 0,
    }

    # Get list of enabled services
    enabled_services = set()
    if services_enabled.exists():
        for yml in services_enabled.glob("*.yml"):
            enabled_services.add(yml.stem)

    # Scan available services
    if not services_available.exists():
        return results, stats

    for yml_file in sorted(services_available.glob("*.yml")):
        service_name = yml_file.stem

        # Skip if filtering to enabled only
        if enabled_only and service_name not in enabled_services:
            continue

        result = parse_service_yaml(yml_file)
        result["enabled"] = service_name in enabled_services

        results.append(result)
        stats["total"] += 1

        if result["has_healthcheck"]:
            stats["with_healthcheck"] += 1
        if result["has_autoheal"]:
            stats["with_autoheal"] += 1
        if result["has_autoheal"] and not result["has_healthcheck"]:
            stats["autoheal_no_healthcheck"] += 1

    return results, stats


def print_text_report(results: list[dict], stats: dict) -> None:
    """Print human-readable audit report."""
    logger.info("=" * 60)
    logger.info("HEALTH CHECK AUDIT REPORT")
    logger.info("=" * 60)
    logger.info("")

    # Statistics
    logger.info("STATISTICS")
    logger.info("-" * 40)
    logger.info(f"Total services scanned: {stats['total']}")
    logger.info(f"With health checks: {stats['with_healthcheck']}")
    logger.info(f"With autoheal label: {stats['with_autoheal']}")
    logger.info(f"Autoheal WITHOUT healthcheck: {stats['autoheal_no_healthcheck']}")
    logger.info("")

    if stats["total"] > 0:
        coverage = (stats["with_healthcheck"] / stats["total"]) * 100
        logger.info(f"Health check coverage: {coverage:.1f}%")
        logger.info("")

    # Critical: autoheal without healthcheck
    critical = [r for r in results if r["has_autoheal"] and not r["has_healthcheck"]]
    if critical:
        logger.info("CRITICAL: Services with autoheal but NO healthcheck")
        logger.info("-" * 40)
        for r in critical:
            status = "[enabled]" if r["enabled"] else "[available]"
            logger.info(f"  {status} {r['service']}")
        logger.info("")

    # Services without health checks (enabled only)
    no_healthcheck = [
        r for r in results if not r["has_healthcheck"] and r["enabled"]
    ]
    if no_healthcheck:
        logger.info("ENABLED services without health checks")
        logger.info("-" * 40)
        for r in no_healthcheck:
            autoheal = " (autoheal)" if r["has_autoheal"] else ""
            logger.info(f"  {r['service']}{autoheal}")
        logger.info("")

    # Services with health checks
    with_healthcheck = [r for r in results if r["has_healthcheck"]]
    if with_healthcheck:
        logger.info("Services WITH health checks")
        logger.info("-" * 40)
        for r in with_healthcheck:
            status = "[enabled]" if r["enabled"] else "[available]"
            logger.info(f"  {status} {r['service']}")
        logger.info("")


def print_json_report(results: list[dict], stats: dict) -> None:
    """Print JSON audit report."""
    report = {
        "statistics": stats,
        "services": results,
        "critical": [
            r["service"]
            for r in results
            if r["has_autoheal"] and not r["has_healthcheck"]
        ],
    }
    logger.info(json.dumps(report, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit services for health check configuration"
    )
    parser.add_argument(
        "--enabled-only",
        action="store_true",
        help="Only audit enabled services",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--base-dir",
        default="/app",
        help="Base directory (default: /app)",
    )

    args = parser.parse_args()
    
    # Setup logging
    setup_logging(level="INFO", enable_colors=True)
    base_dir = Path(args.base_dir)

    results, stats = audit_services(base_dir, args.enabled_only)

    if args.format == "json":
        print_json_report(results, stats)
    else:
        print_text_report(results, stats)

    # Return non-zero if there are critical issues
    return 1 if stats["autoheal_no_healthcheck"] > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
