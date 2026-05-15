# Dockpeek

> Docker Port Dashboard for Easy Container Access

## Links
- [Official Repository](https://github.com/dockpeek/dockpeek)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dockpeek.yml)

## Docker Images
- `ghcr.io/dockpeek/dockpeek:${DOCKPEEK_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKPEEK_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DOCKPEEK_CONTAINER_NAME` |  | Container name |
| `DOCKPEEK_DOCKER_TAG` |  | Docker image tag/version |
| `DOCKPEEK_HOST_NAME` |  | Dockpeek host name |
| `DOCKPEEK_MEM_LIMIT` |  | Dockpeek mem limit |
| `DOCKPEEK_PASSWORD` |  | Service password |
| `DOCKPEEK_RESTART` |  | Container restart policy |
| `DOCKPEEK_SECRET_KEY` |  | Dockpeek secret key |
| `DOCKPEEK_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `DOCKPEEK_USERNAME` |  | Service username |
| `DOCKPEEK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DOCKPEEK_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.dockpeek.entrypoints=websecure`
- `traefik.http.routers.dockpeek.rule=Host(`${DOCKPEEK_HOST_NAME:-dockpeek}.${HOST_DOMAIN}`)`
- `traefik.http.services.dockpeek.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCKPEEK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DOCKPEEK_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${DOCKPEEK_HOST_NAME:-dockpeek}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable dockpeek

# Configure environment variables (if needed)
make scaffold dockpeek

# Start the service
make up
```
