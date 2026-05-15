# Seerr

> Media request and discovery tool for Plex, Jellyfin, and Emby

## Links
- [Official Repository](https://github.com/seerr-team/seerr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/seerr.yml)

## Docker Images
- `ghcr.io/seerr-team/seerr:${SEERR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SEERR_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `SEERR_CONTAINER_NAME` |  | Container name |
| `SEERR_DOCKER_TAG` |  | Docker image tag/version |
| `SEERR_RESTART` |  | Container restart policy |
| `SEERR_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `SEERR_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/seerr:/app/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SEERR_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.seerr.entrypoints=websecure`
- `traefik.http.routers.seerr.rule=Host(`${SEERR_CONTAINER_NAME:-seerr}.${HOST_DOMAIN}`)`
- `traefik.http.services.seerr.loadbalancer.server.port=5055`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SEERR_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${SEERR_AUTOHEAL:-true}`
- `joyride.host.name=${SEERR_CONTAINER_NAME:-seerr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable seerr

# Configure environment variables (if needed)
make scaffold seerr

# Start the service
make up
```
