# Dockpeek Socket Proxy

> Proxy service for Dockpeek

## Links
- [Official Repository](https://github.com/dockpeek/dockpeek)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dockpeek-socket-proxy.yml)

## Docker Images
- `lscr.io/linuxserver/socket-proxy:${DOCKPEEK_SOCKET_PROXY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKPEEK_SOCKET_PROXY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DOCKPEEK_SOCKET_PROXY_CONTAINER_NAME` |  | Container name |
| `DOCKPEEK_SOCKET_PROXY_DOCKER_TAG` |  | Docker image tag/version |
| `DOCKPEEK_SOCKET_PROXY_MEM_LIMIT` |  | Dockpeek socket proxy mem limit |
| `DOCKPEEK_SOCKET_PROXY_RESTART` |  | Container restart policy |
| `DOCKPEEK_SOCKET_PROXY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `2375:2375`

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCKPEEK_SOCKET_PROXY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DOCKPEEK_SOCKET_PROXY_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable dockpeek-socket-proxy

# Configure environment variables (if needed)
make scaffold dockpeek-socket-proxy

# Start the service
make up
```
