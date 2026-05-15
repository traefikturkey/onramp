# Drawio

> A client side editor for "general" diagramming

## Links
- [Official Repository](https://github.com/jgraph/drawio)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/drawio.yml)

## Docker Images
- `jgraph/drawio:${DRAW_IO_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DRAW_IO_CONTAINER_NAME` |  | Container name |
| `DRAW_IO_DOCKER_TAG` |  | Docker image tag/version |
| `DRAW_IO_RESTART` |  | Container restart policy |
| `DRAW_IO_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.drawio.entrypoints=websecure`
- `traefik.http.routers.drawio.rule=Host(`${DRAW_IO_CONTAINER_NAME:-drawio}.${HOST_DOMAIN}`)`
- `traefik.http.services.drawio.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DRAW_IO_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${DRAW_IO_CONTAINER_NAME:-drawio}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable drawio

# Configure environment variables (if needed)
make scaffold drawio

# Start the service
make up
```
