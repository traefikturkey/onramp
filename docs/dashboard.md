# OnRamp Dashboard

The OnRamp Dashboard is a web-based interface for managing your homelab services. It provides real-time container status, service management, and quick access to common operations.

## Features

- **Real-time Container Status** - View running/stopped state, health checks, and resource usage
- **Service Management** - Enable, disable, start, stop, and restart services
- **Container Logs** - View container logs with live streaming
- **Service Categories** - Browse services by category (media, management, network, etc.)
- **Search & Filter** - Quickly find services across your homelab
- **Responsive Design** - Works on desktop and mobile devices

## Installation

Enable the dashboard service:

```bash
make enable-service onramp-dashboard
make restart
```

The dashboard will be available at `https://dashboard.yourdomain.com` (configured via `HOST_DOMAIN`).

## Configuration

Configuration is done via environment variables in `services-enabled/onramp-dashboard.env`:

| Variable | Default | Description |
|----------|---------|-------------|
| `ONRAMP_DASHBOARD_HOST_NAME` | `dashboard` | Subdomain for the dashboard |
| `ONRAMP_DASHBOARD_DEBUG` | `false` | Enable debug mode (shows API docs at `/api/docs`) |
| `ONRAMP_DASHBOARD_MEM_LIMIT` | `256m` | Container memory limit |
| `ONRAMP_DASHBOARD_RESTART` | `unless-stopped` | Container restart policy |
| `ONRAMP_DASHBOARD_TRAEFIK_ENABLE` | `true` | Enable Traefik reverse proxy |
| `ONRAMP_DASHBOARD_WATCHTOWER` | `true` | Enable Watchtower auto-updates |
| `ONRAMP_DASHBOARD_AUTOHEAL` | `true` | Enable Autoheal for unhealthy containers |

### Changing the Subdomain

To access the dashboard at a different subdomain (e.g., `admin.yourdomain.com`):

```bash
make edit-env onramp-dashboard
```

Set:
```
ONRAMP_DASHBOARD_HOST_NAME=admin
```

Then restart:
```bash
make restart-service onramp-dashboard
```

## Usage

### Dashboard Home

The main page shows:
- **Service Grid** - All enabled services with status indicators
- **Quick Actions** - Start, stop, restart buttons for each container
- **Health Status** - Green (healthy), yellow (unhealthy), red (stopped)

### Container Operations

| Action | Description |
|--------|-------------|
| **Start** | Start a stopped container |
| **Stop** | Stop a running container |
| **Restart** | Restart a running container |
| **Logs** | View container stdout/stderr logs |

> **Note:** Core services like Traefik cannot be stopped from the dashboard to prevent accidental lockouts.

### Service Management

Navigate to `/services` to:
- View all available services (enabled and disabled)
- Enable new services
- Disable running services
- View service metadata (description, category, documentation links)

### Viewing Logs

Click the logs icon on any container to view recent logs. Logs update in real-time via server-sent events.

## API

When debug mode is enabled (`ONRAMP_DASHBOARD_DEBUG=true`), API documentation is available at:
- Swagger UI: `https://dashboard.yourdomain.com/api/docs`
- ReDoc: `https://dashboard.yourdomain.com/api/redoc`

### API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/docker/containers` | List all containers |
| `GET /api/docker/containers/{name}` | Get container details |
| `POST /api/docker/containers/{name}/start` | Start container |
| `POST /api/docker/containers/{name}/stop` | Stop container |
| `POST /api/docker/containers/{name}/restart` | Restart container |
| `GET /api/docker/containers/{name}/logs` | Get container logs |
| `GET /api/services/available` | List available services |
| `GET /api/services/enabled` | List enabled services |
| `GET /api/system/health` | Health check |
| `GET /api/system/stats` | System statistics |

## Dashboard Icons

The dashboard shows the official logo/icon for each service on the home page, service catalog, enabled services list, and service detail page. Icons are sourced from the [selfhst/icons](https://github.com/selfhst/icons) collection and are served locally as SVG files so the dashboard works without internet access.

### How Icons Are Matched

Service names in OnRamp are mapped to upstream icon references in `sietch/dashboard/core/icons.py`. When a service name doesn't match an upstream icon exactly, a manual override or a suffix-stripping fallback is used. Services without a matching SVG upstream use the generic Docker icon as a fallback.

### Refreshing Icons

If you add a new service or want to update icons after the upstream collection changes, run:

```bash
make download-icons
```

This downloads the latest icon index, resolves each service name, and saves SVG files to `sietch/dashboard/static/icons/<service>.svg`. Each SVG is also normalized so the artwork is centered and fills the same fraction of the canvas, ensuring icons render at a consistent visual size. Rebuild the Sietch image afterward so the new icons are included in the dashboard container:

```bash
make sietch-rebuild
```

### Overriding an Icon

The dashboard picks an icon automatically, but if a service shows the generic Docker icon (or the wrong logo), you can pin it to a specific upstream icon.

**All icon overrides live in one file: `sietch/dashboard/core/icons.py`, in the `MANUAL_ICON_OVERRIDES` dictionary.**

#### Step 1: Find your service name

The service name is the compose filename without the extension. For example:

| File | Service name |
|---|---|
| `services-available/jellyfin.yml` | `jellyfin` |
| `services-available/gitea-runner.yml` | `gitea-runner` |
| `services-available/games/minecraft-bedrock.yml` | `minecraft-bedrock` |

#### Step 2: Find the upstream icon reference

Icons come from the [selfhst/icons](https://github.com/selfhst/icons) collection. Browse [selfh.st/icons](https://selfh.st/icons/) to find the icon, or search the index from your terminal:

```bash
curl -s https://raw.githubusercontent.com/selfhst/icons/main/index.json \
  | python3 -c "import json,sys; [print(f\"{i['Reference']:<30} SVG={i['SVG']}\") for i in json.load(sys.stdin) if 'plex' in i['Reference'].lower()]"
```

Replace `plex` with what you're looking for. The value you need is the **`Reference`** slug, and the entry **must have `SVG=Yes`** — entries without an SVG variant are skipped and the service falls back to the Docker icon.

#### Step 3: Add the override in `sietch/dashboard/core/icons.py`

Open **`sietch/dashboard/core/icons.py`** and add an entry to the `MANUAL_ICON_OVERRIDES` dictionary mapping your service name to the reference:

```python
MANUAL_ICON_OVERRIDES = {
    # ... existing mappings ...
    "myapp": "some-upstream-reference",
}
```

Notes:

- Keys are matched lowercase, so `"MyApp"` and `"myapp"` are equivalent; use lowercase for consistency.
- Multiple services can share one icon. For example `gitea-runner` maps to `gitea`.
- Map a service to `"docker"` explicitly if you want to force the generic icon.

#### Step 4: Refresh the icons and rebuild

```bash
make download-icons
make restart-service onramp-dashboard
```

The download output shows exactly which reference each service resolved to, so you can confirm your override took effect:

```text
myapp: some-upstream-reference.svg
```

#### Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| Still shows the Docker icon | The reference has `SVG=No` upstream | Pick a different reference that has an SVG variant |
| Still shows the Docker icon | Override key doesn't match the service filename | The key must equal the `.yml` filename minus extension, lowercased |
| Download says `using fallback 'docker'` | Reference slug is misspelled | Re-check the slug in `index.json` |
| Icon didn't change after rebuild | Browser cache | Hard-refresh the page (Ctrl+Shift+R) |
| No matching icon exists upstream | Collection doesn't have one | Keep the `"docker"` fallback, or request the icon in the [selfhst/icons](https://github.com/selfhst/icons/issues) repo |

## Architecture

The dashboard is built with:
- **FastAPI** - Modern Python web framework
- **HTMX** - Dynamic UI without JavaScript frameworks
- **Pico CSS** - Minimal CSS framework
- **Docker SDK** - Container management via Docker socket

The dashboard container has:
- Read-only access to service definitions (`services-available/`, `services-scaffold/`)
- Read-write access to enabled services and configs (`services-enabled/`, `etc/`)
- Read-only access to Docker socket for container management

## Troubleshooting

### Dashboard Not Loading

1. Check if the container is running:
   ```bash
   docker ps | grep onramp-dashboard
   ```

2. Check container logs:
   ```bash
   make logs onramp-dashboard
   ```

3. Verify Traefik is routing correctly:
   ```bash
   docker logs traefik 2>&1 | grep dashboard
   ```

### Container Operations Fail

1. Verify Docker socket is mounted:
   ```bash
   docker exec onramp-dashboard ls -la /var/run/docker.sock
   ```

2. Check container permissions (PUID/PGID should match host user)

### API Errors

Enable debug mode to see detailed error messages:
```bash
make edit-env onramp-dashboard
# Set ONRAMP_DASHBOARD_DEBUG=true
make restart-service onramp-dashboard
```

## Development

For local development without Docker:

```bash
cd sietch
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# Run with hot reload
uvicorn dashboard.app:app --factory --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Via make
make sietch-test

# With coverage
make sietch-test-cov

# Directly
./sietch/run-tests.sh
```

Tests use pytest with mocked Docker and service manager fixtures. See `sietch/tests/` for examples.
