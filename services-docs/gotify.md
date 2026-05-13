# Gotify

> Self-hosted push notification service

## Links
- [Official Repository](https://github.com/gotify/server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/gotify.yml)

## Docker Images
- `ghcr.io/gotify/server:${GOTIFY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GOTIFY_CONTAINER_NAME` |  | Container name |
| `GOTIFY_DEFAULTUSER_PASS` |  | Service username |
| `GOTIFY_DOCKER_TAG` |  | Docker image tag/version |
| `GOTIFY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/gotify:/app/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.gotify.entrypoints=websecure`
- `traefik.http.routers.gotify.rule=Host(`${GOTIFY_CONTAINER_NAME:-gotify}.${HOST_DOMAIN}`)`
- `traefik.http.services.gotify.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GOTIFY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GOTIFY_CONTAINER_NAME:-gotify}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable gotify

# Configure environment variables (if needed)
make scaffold gotify

# Start the service
make up
```
