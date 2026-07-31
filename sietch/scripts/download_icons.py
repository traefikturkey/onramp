#!/usr/bin/env python3
"""Download selfhst/icons SVG icons for all OnRamp services.

Usage:
    python scripts/download_icons.py

This script fetches the icon index from the selfhst/icons repository, resolves
each OnRamp service name to an upstream SVG icon reference, and saves the icon as
static/icons/<service>.svg. Services with no matching SVG upstream use the
generic docker icon so that every service has a local icon file.

Every downloaded SVG is normalized: the artwork is measured and the file is
rewritten with a transform that centers the artwork and scales it to fill the
canvas uniformly. Without this step the upstream icons render at visibly
different sizes because their internal padding varies widely.
"""

import json
import math
import re
import shutil
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

# Add parent directories so we can import dashboard modules both in Docker and standalone
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "dashboard"))

from dashboard.core.icons import (
    FALLBACK_ICON,
    SELFH_ICONS_INDEX,
    resolve_icon_filename,
)

SVG_NS = "http://www.w3.org/2000/svg"

# Fraction of the canvas the artwork should fill after normalization.
ARTWORK_FILL = 0.90


# ---------------------------------------------------------------------------
# SVG geometry helpers (pure Python, no external dependencies)
# ---------------------------------------------------------------------------

Matrix = tuple[float, float, float, float, float, float]
IDENTITY: Matrix = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0)


def mat_mul(m1: Matrix, m2: Matrix) -> Matrix:
    """Compose two affine matrices (apply m2 first, then m1)."""
    a1, b1, c1, d1, e1, f1 = m1
    a2, b2, c2, d2, e2, f2 = m2
    return (
        a1 * a2 + c1 * b2,
        b1 * a2 + d1 * b2,
        a1 * c2 + c1 * d2,
        b1 * c2 + d1 * d2,
        a1 * e2 + c1 * f2 + e1,
        b1 * e2 + d1 * f2 + f1,
    )


def mat_apply(m: Matrix, x: float, y: float) -> tuple[float, float]:
    a, b, c, d, e, f = m
    return a * x + c * y + e, b * x + d * y + f


def parse_transform(value: str) -> Matrix:
    """Parse an SVG transform attribute into a single affine matrix."""
    m = IDENTITY
    for name, args in re.findall(r"(matrix|translate|scale)\s*\(([^)]*)\)", value):
        nums = [float(n) for n in re.findall(r"-?\d*\.?\d+(?:e[+-]?\d+)?", args)]
        if name == "matrix" and len(nums) == 6:
            t: Matrix = tuple(nums)  # type: ignore[assignment]
        elif name == "translate":
            t = (1.0, 0.0, 0.0, 1.0, nums[0], nums[1] if len(nums) > 1 else 0.0)
        elif name == "scale":
            sx = nums[0]
            sy = nums[1] if len(nums) > 1 else sx
            t = (sx, 0.0, 0.0, sy, 0.0, 0.0)
        else:
            continue
        m = mat_mul(m, t)
    return m


def arc_sample_points(
    x1: float,
    y1: float,
    rx: float,
    ry: float,
    phi_deg: float,
    large_arc: float,
    sweep: float,
    x2: float,
    y2: float,
    n: int = 12,
) -> list[tuple[float, float]]:
    """Sample an SVG elliptical arc (endpoint -> center parameterization)."""
    if rx == 0 or ry == 0:
        return [(x2, y2)]
    rx, ry = abs(rx), abs(ry)
    phi = math.radians(phi_deg % 360)
    cos_p, sin_p = math.cos(phi), math.sin(phi)

    dx, dy = (x1 - x2) / 2.0, (y1 - y2) / 2.0
    x1p = cos_p * dx + sin_p * dy
    y1p = -sin_p * dx + cos_p * dy

    lam = x1p**2 / rx**2 + y1p**2 / ry**2
    if lam > 1.0:
        s = math.sqrt(lam)
        rx, ry = rx * s, ry * s

    num = rx**2 * ry**2 - rx**2 * y1p**2 - ry**2 * x1p**2
    den = rx**2 * y1p**2 + ry**2 * x1p**2
    coef = math.sqrt(max(num / den, 0.0))
    if large_arc == sweep:
        coef = -coef
    cxp = coef * rx * y1p / ry
    cyp = -coef * ry * x1p / rx

    cx = cos_p * cxp - sin_p * cyp + (x1 + x2) / 2.0
    cy = sin_p * cxp + cos_p * cyp + (y1 + y2) / 2.0

    def angle(ux: float, uy: float, vx: float, vy: float) -> float:
        d = math.hypot(ux, uy) * math.hypot(vx, vy)
        c = max(-1.0, min(1.0, (ux * vx + uy * vy) / d))
        a = math.acos(c)
        return -a if ux * vy - uy * vx < 0 else a

    theta1 = angle(1.0, 0.0, (x1p - cxp) / rx, (y1p - cyp) / ry)
    dtheta = angle(
        (x1p - cxp) / rx,
        (y1p - cyp) / ry,
        (-x1p - cxp) / rx,
        (-y1p - cyp) / ry,
    )
    if not sweep and dtheta > 0:
        dtheta -= 2 * math.pi
    elif sweep and dtheta < 0:
        dtheta += 2 * math.pi

    pts = []
    for k in range(n + 1):
        t = theta1 + dtheta * k / n
        pts.append(
            (
                cx + rx * math.cos(t) * cos_p - ry * math.sin(t) * sin_p,
                cy + rx * math.cos(t) * sin_p + ry * math.sin(t) * cos_p,
            )
        )
    return pts


def path_points(d: str) -> list[tuple[float, float]]:
    """Return bounding-relevant points from SVG path data.

    Includes segment endpoints, curve control points (the curve lies within the
    convex hull of its control polygon) and sampled arc points.
    """
    tokens = re.findall(r"[MmLlHhVvCcSsQqTtAaZz]|-?\d*\.?\d+(?:e[+-]?\d+)?", d)
    i = 0
    cx = cy = sx = sy = 0.0
    pts: list[tuple[float, float]] = []
    cmd = ""
    nargs = {"M": 2, "L": 2, "H": 1, "V": 1, "C": 6, "S": 4, "Q": 4, "T": 2, "A": 7, "Z": 0}

    def read(n: int) -> list[float]:
        nonlocal i
        vals = [float(tokens[i + j]) for j in range(n)]
        i += n
        return vals

    while i < len(tokens):
        if re.match(r"[A-Za-z]", tokens[i]):
            cmd = tokens[i]
            i += 1
            if cmd in "Zz":
                cx, cy = sx, sy
                continue
        n = nargs[cmd.upper()]
        vals = read(n)
        rel = cmd.islower()
        u = cmd.upper()

        if u == "M":
            x, y = (vals[0] + cx, vals[1] + cy) if rel else (vals[0], vals[1])
            cx, cy = sx, sy = x, y
            pts.append((x, y))
            cmd = "l" if rel else "L"  # implicit lineto after moveto
        elif u == "L":
            x, y = (vals[0] + cx, vals[1] + cy) if rel else (vals[0], vals[1])
            cx, cy = x, y
            pts.append((x, y))
        elif u == "H":
            cx = vals[0] + cx if rel else vals[0]
            pts.append((cx, cy))
        elif u == "V":
            cy = vals[0] + cy if rel else vals[0]
            pts.append((cx, cy))
        elif u == "C":
            x1, y1, x2, y2, x, y = vals
            if rel:
                x1, y1, x2, y2, x, y = x1 + cx, y1 + cy, x2 + cx, y2 + cy, x + cx, y + cy
            pts.extend([(x1, y1), (x2, y2), (x, y)])
            cx, cy = x, y
        elif u == "S":
            x2, y2, x, y = vals
            if rel:
                x2, y2, x, y = x2 + cx, y2 + cy, x + cx, y + cy
            pts.extend([(x2, y2), (x, y)])
            cx, cy = x, y
        elif u == "Q":
            x1, y1, x, y = vals
            if rel:
                x1, y1, x, y = x1 + cx, y1 + cy, x + cx, y + cy
            pts.extend([(x1, y1), (x, y)])
            cx, cy = x, y
        elif u == "T":
            x, y = (vals[0] + cx, vals[1] + cy) if rel else (vals[0], vals[1])
            cx, cy = x, y
            pts.append((x, y))
        elif u == "A":
            rx, ry, rot, laf, swp, x, y = vals
            if rel:
                x, y = x + cx, y + cy
            pts.extend(arc_sample_points(cx, cy, rx, ry, rot, laf, swp, x, y))
            cx, cy = x, y
    return pts


def shape_points(elem: ET.Element, tag: str) -> list[tuple[float, float]]:
    """Return bounding-relevant points for a single SVG shape element."""
    if tag == "path":
        return path_points(elem.get("d", ""))
    if tag == "circle":
        cx = float(elem.get("cx", 0))
        cy = float(elem.get("cy", 0))
        r = float(elem.get("r", 0))
        return [(cx - r, cy - r), (cx + r, cy + r)]
    if tag == "ellipse":
        cx = float(elem.get("cx", 0))
        cy = float(elem.get("cy", 0))
        rx = float(elem.get("rx", 0))
        ry = float(elem.get("ry", 0))
        return [(cx - rx, cy - ry), (cx + rx, cy + ry)]
    if tag == "rect":
        x = float(elem.get("x", 0))
        y = float(elem.get("y", 0))
        w = float(elem.get("width", 0))
        h = float(elem.get("height", 0))
        return [(x, y), (x + w, y + h)]
    if tag in ("polygon", "polyline"):
        nums = [float(n) for n in re.findall(r"-?\d*\.?\d+", elem.get("points", ""))]
        return list(zip(nums[0::2], nums[1::2]))
    if tag == "line":
        return [
            (float(elem.get("x1", 0)), float(elem.get("y1", 0))),
            (float(elem.get("x2", 0)), float(elem.get("y2", 0))),
        ]
    return []


def svg_artwork_bounds(root: ET.Element) -> tuple[float, float, float, float] | None:
    """Compute the bounding box of all artwork in an SVG document."""
    all_pts: list[tuple[float, float]] = []

    def walk(elem: ET.Element, matrix: Matrix) -> None:
        m = mat_mul(matrix, parse_transform(elem.get("transform", "")))
        tag = elem.tag.split("}")[-1]
        for x, y in shape_points(elem, tag):
            all_pts.append(mat_apply(m, x, y))
        for child in elem:
            walk(child, m)

    walk(root, IDENTITY)
    if not all_pts:
        return None
    xs = [p[0] for p in all_pts]
    ys = [p[1] for p in all_pts]
    return min(xs), min(ys), max(xs), max(ys)


# ---------------------------------------------------------------------------
# Normalization
# ---------------------------------------------------------------------------


def normalize_svg(svg_path: Path, fill: float = ARTWORK_FILL) -> bool:
    """Rewrite an SVG so its artwork is centered and fills the canvas uniformly.

    The upstream collection draws each logo at a different scale within the
    viewBox, so icons render at visibly different sizes when placed in a fixed
    box. Wrapping the content in a computed transform makes every icon fill the
    same fraction of the canvas. Returns True if the file was normalized.
    """
    ET.register_namespace("", SVG_NS)
    try:
        tree = ET.parse(svg_path)
    except ET.ParseError:
        return False
    root = tree.getroot()

    viewbox = root.get("viewBox")
    if not viewbox:
        return False
    vb = [float(n) for n in re.findall(r"-?\d*\.?\d+", viewbox)]
    if len(vb) != 4:
        return False
    vx, vy, vw, vh = vb

    bounds = svg_artwork_bounds(root)
    if bounds is None:
        return False
    x0, y0, x1, y1 = bounds
    bw, bh = x1 - x0, y1 - y0
    if bw <= 0 or bh <= 0:
        return False

    target = min(vw, vh) * fill
    scale = target / max(bw, bh)
    cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
    tx = vx + vw / 2.0 - cx * scale
    ty = vy + vh / 2.0 - cy * scale

    group = ET.Element(f"{{{SVG_NS}}}g")
    group.set("transform", f"translate({tx:.3f} {ty:.3f}) scale({scale:.6f})")
    for child in list(root):
        root.remove(child)
        group.append(child)
    root.append(group)

    tree.write(svg_path, encoding="unicode", xml_declaration=True)
    return True


# ---------------------------------------------------------------------------
# Downloading
# ---------------------------------------------------------------------------


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
    """Download and normalize SVG icons for all services."""
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
        normalize_svg(fallback_source)
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
            if not normalize_svg(dest):
                print(f"  WARNING: Could not normalize {dest.name}")
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
