# Overseerr

> Request management and notification system for media content

## Links
- [Official Repository](https://github.com/linuxserver/docker-overseerr)
- [Docker Image](https://hub.docker.com/r/linuxserver/overseerr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/overseerr.yml)

## Docker Images
- `lscr.io/linuxserver/overseerr:${OVERSEERR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OVERSEERR_CONTAINER_NAME` |  | Container name |
| `OVERSEERR_DOCKER_TAG` |  | Docker image tag/version |
| `OVERSEERR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `5055:5055`

### Volumes
- `./etc/overseerr:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.overseerr.entrypoints=websecure`
- `traefik.http.routers.overseerr.rule=Host(`${OVERSEERR_CONTAINER_NAME:-overseerr}.${HOST_DOMAIN}`)`
- `traefik.http.services.overseerr.loadbalancer.server.port=5055`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OVERSEERR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${OVERSEERR_CONTAINER_NAME:-overseerr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable overseerr

# Configure environment variables (if needed)
make scaffold overseerr

# Start the service
make up
```
