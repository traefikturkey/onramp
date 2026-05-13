# Docker Proxy

> Proxy for docker containers

## Links
- [Official Repository](https://github.com/Tecnativa/docker-socket-proxy)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/docker-proxy.yml)

## Docker Images
- `tecnativa/docker-socket-proxy:${DOCKER_PROXY_DOCKER_TAG:-0.2.0}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKER_PROXY_CONTAINER_NAME` |  | Container name |
| `DOCKER_PROXY_DOCKER_TAG` |  | Docker image tag/version |
| `DOCKER_PROXY_INTERFACE_IP` |  | Docker proxy interface ip |
| `DOCKER_PROXY_INTERFACE_PORT` |  | Service port number |
| `DOCKER_PROXY_LOG_LEVEL` |  | Docker proxy log level |
| `DOCKER_PROXY_RESTART` |  | Container restart policy |
| `DOCKER_PROXY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${DOCKER_PROXY_INTERFACE_IP:-127.0.0.1}:${DOCKER_PROXY_INTERFACE_PORT:-2375}:2375`

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Labels
**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCKER_PROXY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable docker-proxy

# Configure environment variables (if needed)
make scaffold docker-proxy

# Start the service
make up
```
