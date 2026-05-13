# Windows

> Windows inside a Docker container.

## Links
- [Official Repository](https://github.com/dockur/windows)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/windows.yml)

## Docker Images
- `ghcr.io/dockur/windows:${WINDOWS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WINDOWS_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `WINDOWS_CONTAINER_NAME` |  | Container name |
| `WINDOWS_DOCKER_TAG` |  | Docker image tag/version |
| `WINDOWS_HOST_NAME` |  | Windows host name |
| `WINDOWS_MEM_LIMIT` |  | Windows mem limit |
| `WINDOWS_RESTART` |  | Container restart policy |
| `WINDOWS_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `WINDOWS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/windows:/storage` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${WINDOWS_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.windows.entrypoints=websecure`
- `traefik.http.routers.windows.rule=Host(`${WINDOWS_HOST_NAME:-windows}.${HOST_DOMAIN}`)`
- `traefik.http.services.windows.loadbalancer.server.port=8006`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WINDOWS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${WINDOWS_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${WINDOWS_HOST_NAME:-windows}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable windows

# Configure environment variables (if needed)
make scaffold windows

# Start the service
make up
```
