# Dashdot

> Dashboard for monitoring docker containers

## Links
- [Official Repository](https://github.com/MauriceNino/dashdot)
- [Official Documentation](https://getdashdot.com/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dashdot.yml)

## Docker Images
- `mauricenino/dashdot:${DASHDOT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DASHDOT_CONTAINER_NAME` |  | Container name |
| `DASHDOT_DOCKER_TAG` |  | Docker image tag/version |
| `DASHDOT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
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
- `traefik.http.routers.dashdot.entrypoints=websecure`
- `traefik.http.routers.dashdot.rule=Host(`${DASHDOT_CONTAINER_NAME:-dashdot}.${HOST_DOMAIN}`)`
- `traefik.http.services.dashdot.loadbalancer.server.port=3001`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DASHDOT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${DASHDOT_CONTAINER_NAME:-dashdot}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable dashdot

# Configure environment variables (if needed)
make scaffold dashdot

# Start the service
make up
```
