# Kimai

> Time-tracking software for freelancers and small businesses

## Links
- [Official Repository](https://github.com/tobybatch/kimai2)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/kimai.yml)

## Docker Images
- `kimai/kimai2:${KIMAI_DOCKER_TAG:-apache}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KIMAI_CONTAINER_NAME` |  | Container name |
| `KIMAI_DOCKER_TAG` |  | Docker image tag/version |
| `KIMAI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
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
- `traefik.http.routers.kimai.entrypoints=websecure`
- `traefik.http.routers.kimai.rule=Host(`${KIMAI_CONTAINER_NAME:-kimai}.${HOST_DOMAIN}`)`
- `traefik.http.services.kimai.loadbalancer.server.port=8001`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KIMAI_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${KIMAI_CONTAINER_NAME:-kimai}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable kimai

# Configure environment variables (if needed)
make scaffold kimai

# Start the service
make up
```
