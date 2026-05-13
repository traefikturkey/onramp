# Whoami

> Simple web service that returns information about the host

## Links
- [Docker Image](https://hub.docker.com/r/traefik/whoami)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/whoami.yml)

## Docker Images
- `ghcr.io/traefik/whoami:${WHOAMI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WHOAMI_CONTAINER_NAME` |  | Container name |
| `WHOAMI_DOCKER_TAG` |  | Docker image tag/version |
| `WHOAMI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.whoami.entrypoints=websecure`
- `traefik.http.routers.whoami.rule=Host(`${WHOAMI_CONTAINER_NAME:-whoami}.${HOST_DOMAIN}`)`
- `traefik.http.services.whoami.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WHOAMI_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WHOAMI_CONTAINER_NAME:-whoami}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable whoami

# Configure environment variables (if needed)
make scaffold whoami

# Start the service
make up
```
