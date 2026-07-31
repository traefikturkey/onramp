#!/usr/bin/env python3
"""Download selfhst/icons SVG icons for all OnRamp services.

Usage:
    python scripts/download_icons.py

This script fetches the icon index from the selfhst/icons repository, resolves
each OnRamp service name to an upstream SVG icon reference, and saves the icon as
static/icons/<service>.svg. Services with no matching SVG upstream use the
generic docker icon so that every service has a local icon file.
"""

import json
import shutil
import sys
import urllib.request
from pathlib import Path

# Add parent directories so we can import dashboard modules both in Docker and standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))

from dashboard.core.icons import (
    FALLBACK_ICON,
    SELFH_ICONS_INDEX,
    resolve_icon_filename,
)


def fetch_icon_index() -> dict:
    """Fetch the selfhst/icons index and return a mapping of reference to metadata."""
    print(f"Fetching icon index from {SELFH_ICONS_INDEX}...")
    with urllib.request.urlopen(SELFH_ICONS_INDEX, timeout=60) as response:  # noqa: S310
        data = json.loads(response.read().decode())

    index = {}
    for item in data:
        ref = item.get("Reference")
        if ref:
            index[ref] = item

    print(f"Found {len(index)} upstream icons.")
    return index


def discover_services(base_dir: Path) -> list[str]:
    """Discover all OnRamp services from services-available and games subdirectories."""
    services = []
    services_available = base_dir / "services-available"
    games_dir = services_available / "games"

    for directory in (services_available, games_dir):
        if not directory.exists():
            continue
        for f in sorted(directory.glob("*.yml")):
            services.append(f.stem)

    # Core services that may appear in the dashboard but are not in services-available/
    core_services = ["traefik"]
    for core in core_services:
        if core not in services:
            services.append(core)

    return sorted(set(services))


def download_icon(url: str, dest: Path) -> bool:
    """Download a single icon and save it to dest. Returns True on success."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=30) as response:  # noqa: S310
            data = response.read()
        dest.write_bytes(data)
        return True
    except Exception as e:
        print(f"  WARNING: Failed to download {url}: {e}")
        return False


def main() -> int:
    """Download SVG icons for all services."""
    # The script is typically run from the repository root (e.g. make download-icons).
    # Use the current working directory if it looks like the repo root, otherwise
    # fall back to the location of this script (sietch/scripts/download_icons.py).
    cwd = Path.cwd()
    script_fallback = Path(__file__).resolve().parent.parent.parent
    repo_root = cwd if (cwd / "services-available").exists() else script_fallback

    icons_dir = repo_root / "sietch" / "dashboard" / "static" / "icons"
    icons_dir.mkdir(parents=True, exist_ok=True)

    index = fetch_icon_index()
    upstream_icons = set(index.keys())
    services = discover_services(repo_root)
    print(f"Discovered {len(services)} services.")

    # Determine which upstream refs have an SVG variant available
    refs_with_svg = {
        ref for ref, meta in index.items() if meta.get("SVG") == "Yes"
    }

    # Ensure the fallback icon is present
    fallback_source = icons_dir / f"{FALLBACK_ICON}.svg"
    fallback_cdn = (
        "https://cdn.jsdelivr.net/gh/selfhst/icons@main/svg/"
        f"{FALLBACK_ICON}.svg"
    )
    fallback_downloaded = download_icon(fallback_cdn, fallback_source)
    if fallback_downloaded:
        print(f"fallback: {FALLBACK_ICON}.svg")
    else:
        print(f"  WARNING: Could not download fallback icon {FALLBACK_ICON}.svg")

    stats = {"downloaded": 0, "fallback": 0, "errors": 0}

    for service in services:
        upstream_name = resolve_icon_filename(service, upstream_icons)
        has_svg = upstream_name in refs_with_svg
        dest = icons_dir / f"{service}.svg"

        if upstream_name == FALLBACK_ICON or not has_svg:
            # No specific SVG available; copy the generic fallback icon
            stats["fallback"] += 1
            print(f"{service}: using fallback '{FALLBACK_ICON}'")
            if fallback_source.exists():
                shutil.copy2(fallback_source, dest)
            continue

        cdn_url = (
            "https://cdn.jsdelivr.net/gh/selfhst/icons@main/svg/"
            f"{upstream_name}.svg"
        )

        print(f"{service}: {upstream_name}.svg")

        if download_icon(cdn_url, dest):
            stats["downloaded"] += 1
        else:
            stats["errors"] += 1
            if fallback_source.exists():
                shutil.copy2(fallback_source, dest)
                print(f"{service}: copied fallback icon")

    print(
        f"\nDone: {stats['downloaded']} downloaded, "
        f"{stats['fallback']} fallback, {stats['errors']} errors"
    )
    return 0 if stats["errors"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
