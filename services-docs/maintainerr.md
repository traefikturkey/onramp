# Maintainerr

> managing media library

## Links
- [Official Repository](https://github.com/jorenn92/Maintainerr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/maintainerr.yml)

## Docker Images
- `ghcr.io/jorenn92/maintainerr:${MAINTAINERR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MAINTAINERR_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `MAINTAINERR_CONTAINER_NAME` |  | Container name |
| `MAINTAINERR_DOCKER_TAG` |  | Docker image tag/version |
| `MAINTAINERR_RESTART` |  | Container restart policy |
| `MAINTAINERR_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `MAINTAINERR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/maintainerr:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${MAINTAINERR_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.maintainerr.entrypoints=websecure`
- `traefik.http.routers.maintainerr.rule=Host(`${MAINTAINERR_CONTAINER_NAME:-maintainerr}.${HOST_DOMAIN}`)`
- `traefik.http.services.maintainerr.loadbalancer.server.port=6246`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MAINTAINERR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${MAINTAINERR_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${MAINTAINERR_CONTAINER_NAME:-maintainerr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable maintainerr

# Configure environment variables (if needed)
make scaffold maintainerr

# Start the service
make up
```
