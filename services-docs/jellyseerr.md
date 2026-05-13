# Jellyseerr

> Container for running jellyseerr, a torrent indexer

## Links
- [Official Repository](https://github.com/Fallenbagel/jellyseerr/tree/develop)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/jellyseerr.yml)

## Docker Images
- `fallenbagel/jellyseerr:${JELLYSEERR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `JELLYSEERR_CONTAINER_NAME` |  | Container name |
| `JELLYSEERR_DOCKER_TAG` |  | Docker image tag/version |
| `JELLYSEERR_RESTART` |  | Container restart policy |
| `JELLYSEERR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/jellyseerr:/app/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.jellyseerr.entrypoints=websecure`
- `traefik.http.routers.jellyseerr.rule=Host(`${JELLYSEERR_CONTAINER_NAME:-jellyseerr}.${HOST_DOMAIN}`)`
- `traefik.http.services.jellyseerr.loadbalancer.server.port=5055`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${JELLYSEERR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${JELLYSEERR_CONTAINER_NAME:-jellyseerr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable jellyseerr

# Configure environment variables (if needed)
make scaffold jellyseerr

# Start the service
make up
```
