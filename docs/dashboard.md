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
