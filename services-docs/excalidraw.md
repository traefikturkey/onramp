# Excalidraw

> Collaborative whiteboard tool

## Links
- [Official Repository](https://github.com/excalidraw and https://github.com/excalidraw/excalidraw)
- [Docker Image](https://hub.docker.com/r/excalidraw/excalidraw)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/excalidraw.yml)

## Docker Images
- `excalidraw/excalidraw:${EXCALIDRAW_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `EXCALIDRAW_CONTAINER_NAME` |  | Container name |
| `EXCALIDRAW_DOCKER_TAG` |  | Docker image tag/version |
| `EXCALIDRAW_RESTART` |  | Container restart policy |
| `EXCALIDRAW_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
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
- `traefik.http.routers.excalidraw.entrypoints=websecure`
- `traefik.http.routers.excalidraw.rule=Host(`${EXCALIDRAW_CONTAINER_NAME:-excalidraw}.${HOST_DOMAIN}`)`
- `traefik.http.services.excalidraw.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${EXCALIDRAW_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${EXCALIDRAW_CONTAINER_NAME:-excalidraw}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable excalidraw

# Configure environment variables (if needed)
make scaffold excalidraw

# Start the service
make up
```
