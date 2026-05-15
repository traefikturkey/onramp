# Vert

> The next-generation file converter. Open source, fully local

## Links
- [Official Repository](https://github.com/VERT-sh/VERT)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/vert.yml)

## Docker Images
- `ghcr.io/vert-sh/vert:${VERT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `VERT_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `VERT_CONTAINER_NAME` |  | Container name |
| `VERT_DOCKER_TAG` |  | Docker image tag/version |
| `VERT_HOST_NAME` |  | Vert host name |
| `VERT_MEM_LIMIT` |  | Vert mem limit |
| `VERT_RESTART` |  | Container restart policy |
| `VERT_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `VERT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/vert/default.conf:/etc/nginx/conf.d/default.conf` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${VERT_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.vert.entrypoints=websecure`
- `traefik.http.routers.vert.rule=Host(`${VERT_HOST_NAME:-vert}.${HOST_DOMAIN}`)`
- `traefik.http.services.vert.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${VERT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${VERT_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${VERT_HOST_NAME:-vert}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable vert

# Configure environment variables (if needed)
make scaffold vert

# Start the service
make up
```
