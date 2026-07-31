"""Icon resolution for OnRamp Dashboard.

Maps OnRamp service names to selfhst/icons (https://github.com/selfhst/icons)
references. Icons are downloaded by scripts/download_icons.py and served locally
from static/icons/<service>.svg. The runtime template code only needs to
reference the local path; the mapping here is used at build/download time to
fetch the correct icon files.
"""

from pathlib import Path

# selfh.st icons index (lists every available reference and supported formats)
SELFH_ICONS_INDEX = (
    "https://raw.githubusercontent.com/selfhst/icons/main/index.json"
)

# Icon used when no specific match can be found or when the upstream icon has no
# SVG variant. selfhst/icons provides an SVG for docker.
FALLBACK_ICON = "docker"

# Manual overrides for service names that do not map 1:1 to a selfhst/icons
# reference, or that have no suitable icon in the upstream collection.
# At runtime the dashboard references /static/icons/<service_name>.svg (or
# /static/icons/docker.svg for services mapped to the fallback).
MANUAL_ICON_OVERRIDES = {
    # --- Valid selfhst/icons references ---
    "actual": "actual-budget",
    "adguard": "adguard-home",
    "airprint": "cups",
    "autokuma": "uptime-kuma",
    "beszel-agent": "beszel",
    "beszel-hub": "beszel",
    "cloudflare-companion.untested": "cloudflare",
    "cloudflare-ddns": "cloudflare",
    "cloudflare-tunnel": "cloudflare",
    "cloudflare-tunnel-gui": "cloudflare",
    "crowdsec-traefik-bouncer": "crowdsec",
    "cv4pve": "proxmox",
    "doku": "dokuwiki",
    "drawio": "draw-io",
    "droneci": "drone-ci",
    "firefly-data-importer": "firefly-iii",
    "firefly3": "firefly-iii",
    "frigate-coral": "frigate",
    "frigate-cpu": "frigate",
    "frigate-nvidia": "frigate",
    "gitea-runner": "gitea",
    "github-backup": "github",
    "homeassistant": "home-assistant",
    "ittools": "it-tools",
    "joplin-api": "joplin",
    "lubelog": "lubelogger",
    "minecraft": "minecraft",
    "minecraft-bedrock": "minecraft",
    "minecraft-direwolf20-119": "minecraft",
    "minecraft-direwolf20-120": "minecraft",
    "minecraft-skyfactory4": "minecraft",
    "mssql": "microsoft-sql-server",
    "n8n-mcp": "n8n",
    "netbootxyz": "netboot-xyz",
    "nodered": "node-red",
    "ollama-webui": "open-webui",
    "paperless-ai": "paperless-ngx",
    "paperless-ngx-postgres": "paperless-ngx",
    "pihole": "pi-hole",
    "playit-docker": "playit-gg",
    "portainer-ee": "portainer",
    "postgres": "postgresql",
    "prometheus-all": "prometheus",
    "prometheus-blackbox-exporter": "prometheus",
    "prometheus-loki": "loki",
    "prometheus-proxmox-exporter": "proxmox",
    "pterodactyl-panel": "pterodactyl",
    "pterodactyl-wings": "pterodactyl",
    "radarr-postgres": "radarr",
    "rwmarkable": "docker",  # no remarkable icon upstream
    "sftp-server": "sftpgo",
    "tandoor": "tandoor-recipes",
    "transmission-vpn": "transmission",
    "ubuntu": "ubuntu",
    "vault": "hashicorp-vault",
    "wg-easy": "wireguard",
    "wikijs": "wiki-js",
    "windows": "microsoft-windows",
    "woodpecker": "woodpecker-ci",
    "youtube-transcript-mcp": "youtube",

    # --- Services with no matching selfhst/icons entry; use the generic fallback ---
    "13ft": "docker",
    "autoheal": "docker",
    "avahi": "docker",
    "basaran": "docker",
    "bind": "docker",
    "bytebase": "docker",
    "cert-dumper": "docker",
    "chromadb": "docker",
    "cially": "docker",
    "claude-connector": "docker",
    "code-server": "docker",
    "coqui-ai": "docker",
    "cup": "docker",
    "dalai": "docker",
    "dockerizalo": "docker",
    "docker-mirror": "docker",
    "docker-proxy": "docker",
    "docker-registry": "docker",
    "dockpeek-socket-proxy": "docker",
    "dozzle-agent": "dozzle",
    "dozzle-path": "dozzle",
    "factorio": "docker",
    "flightcheck": "docker",
    "fooocus": "docker",
    "fossflow": "docker",
    "foundryvtt": "docker",
    "fulltext-rss": "docker",
    "guacamole": "docker",
    "headphones": "docker",
    "hypermind": "docker",
    "infinity": "docker",
    "itflow": "docker",
    "iventoy": "docker",
    "joyride": "docker",
    "kaizoku": "docker",
    "kaneo": "docker",
    "kasm": "docker",
    "lidify": "docker",
    "mailhog": "docker",
    "mailrise": "docker",
    "makemkv": "docker",
    "mediamanager": "docker",
    "mindustry": "docker",
    "monocker": "docker",
    "nebula-sync": "docker",
    "netvisor-daemon": "docker",
    "netvisor": "docker",
    "newsdash": "docker",
    "onboard": "docker",
    "ongoing": "docker",
    "onramp-dashboard": "docker",
    "openbrain": "docker",
    "pipelines": "docker",
    "postfix": "docker",
    "prestashop": "docker",
    "project-zomboid": "docker",
    "pwndrop": "docker",
    "remotely": "docker",
    "samba": "docker",
    "sd-web": "docker",
    "spacebin": "docker",
    "sqliteweb": "docker",
    "streaming-search": "docker",
    "synchronet": "docker",
    "tasktrove": "docker",
    "trilium": "docker",
    "unifi": "docker",
    "unmanic": "docker",
    "valheim": "docker",
    "vert": "docker",
    "wbo": "docker",
    "webmap": "docker",
    "wetty": "docker",
    "whoami": "docker",
    "wireshark": "docker",

    # --- Core services not present in services-available/ ---
    "traefik": "traefik",
}

# Suffixes that can be stripped from a service name when looking for an upstream
# icon. Order matters: longer, more-specific suffixes should be stripped first.
STRIP_SUFFIXES = [
    "-companion.untested",
    "-direwolf20-119",
    "-direwolf20-120",
    "-skyfactory4",
    "-blackbox-exporter",
    "-data-importer",
    "-socket-proxy",
    "-transcript-mcp",
    "-traefik-bouncer",
    "-proxmox-exporter",
    "-node-exporter",
    "-postgres",
    "-postgress",
    "-mariadb",
    "-mysql",
    "-postgre",
    "-webui",
    "-gui",
    "-path",
    "-panel",
    "-wings",
    "-exporter",
    "-alertmanager",
    "-mcp",
    "-api",
    "-daemon",
    "-runner",
    "-backup",
    "-server",
    "-vpn",
    "-docker",
    "-importer",
    "-ai",
    "-all",
    "-loki",
    "-node",
    "-proxmox",
    "-tracker",
    "-pdf",
    "-search",
    "-productivity",
    "-wire",
    "-agent",
    "-hub",
    "-cpu",
    "-coral",
    "-nvidia",
    "-bedrock",
]


def _normalize(name: str) -> str:
    """Normalize a service name for matching."""
    return name.lower().strip()


def _strip_suffixes(name: str) -> list[str]:
    """Generate candidate names by progressively stripping known suffixes."""
    candidates = [name]
    parts = name.split("-")

    for i in range(len(parts) - 1, 0, -1):
        prefix = "-".join(parts[:i])
        if prefix:
            candidates.append(prefix)

    return candidates


def resolve_icon_filename(service_name: str, upstream_icons: set[str]) -> str:
    """Resolve a service name to an available selfhst/icons reference.

    Args:
        service_name: The OnRamp service name (e.g., "plex", "gitea-runner").
        upstream_icons: A set of available icon references from the upstream
            index (the "Reference" field, without the .svg extension).

    Returns:
        The upstream icon reference to download (without the .svg extension).
        Falls back to the generic docker icon if no match is found.
    """
    normalized = _normalize(service_name)

    candidates = [normalized]
    candidates.extend(_strip_suffixes(normalized))

    for candidate in candidates:
        # 1. Explicit manual override
        if candidate in MANUAL_ICON_OVERRIDES:
            override = MANUAL_ICON_OVERRIDES[candidate]
            if override in upstream_icons:
                return override
            # If the override target doesn't exist upstream, continue searching.

        # 2. Direct match in upstream repo
        if candidate in upstream_icons:
            return candidate

    # 3. Ultimate fallback
    return FALLBACK_ICON


def get_icon_filename(service_name: str) -> str:
    """Return the best-guess selfhst/icons reference for a service.

    This is a convenience wrapper that does not require the upstream icon set.
    It uses manual overrides and suffix stripping, then returns the original
    name as a best guess. The download script uses resolve_icon_filename() for
    exact matching against the upstream repo.
    """
    normalized = _normalize(service_name)

    if normalized in MANUAL_ICON_OVERRIDES:
        return MANUAL_ICON_OVERRIDES[normalized]

    for candidate in _strip_suffixes(normalized):
        if candidate in MANUAL_ICON_OVERRIDES:
            return MANUAL_ICON_OVERRIDES[candidate]
        if candidate:
            return candidate

    return FALLBACK_ICON


def get_icon_url(service_name: str) -> str:
    """Return the local static URL for a service's icon."""
    normalized = _normalize(service_name)
    upstream = get_icon_filename(normalized)
    if upstream == FALLBACK_ICON:
        return f"/static/icons/{FALLBACK_ICON}.svg"
    return f"/static/icons/{normalized}.svg"


def get_local_icon_path(service_name: str, base_dir: str = "/app") -> Path:
    """Return the filesystem path where the service icon should be stored."""
    normalized = _normalize(service_name)
    upstream = get_icon_filename(normalized)
    filename = FALLBACK_ICON if upstream == FALLBACK_ICON else normalized
    return Path(base_dir) / "sietch" / "dashboard" / "static" / "icons" / f"{filename}.svg"


def get_upstream_url(service_name: str) -> str:
    """Return the upstream CDN URL for a service's SVG icon."""
    filename = get_icon_filename(service_name)
    return (
        "https://cdn.jsdelivr.net/gh/selfhst/icons@main/svg/"
        f"{filename}.svg"
    )
