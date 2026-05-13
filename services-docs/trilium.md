# Trilium

> Personal knowledge management system (TriliumNext fork)

## Links
- [Official Repository](https://github.com/TriliumNext/Trilium)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/trilium.yml)

## Docker Images
- `ghcr.io/triliumnext/trilium:${TRILIUM_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TRILIUM_CONTAINER_NAME` |  | Container name |
| `TRILIUM_DOCKER_TAG` |  | Docker image tag/version |
| `TRILIUM_RESTART` |  | Container restart policy |
| `TRILIUM_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/trilium:/home/node/trilium-data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.trilium.entrypoints=websecure`
- `traefik.http.routers.trilium.rule=Host(`${TRILIUM_CONTAINER_NAME:-trilium}.${HOST_DOMAIN}`)`
- `traefik.http.services.trilium.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TRILIUM_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${TRILIUM_CONTAINER_NAME:-trilium}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable trilium

# Configure environment variables (if needed)
make scaffold trilium

# Start the service
make up
```
