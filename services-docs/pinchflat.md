# Pinchflat

> Pinchflat is a self-hosted app for downloading YouTube content built using yt-dlp

## Links
- [Official Repository](https://github.com/kieraneglin/pinchflat)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pinchflat.yml)

## Docker Images
- `ghcr.io/kieraneglin/pinchflat:${PINCHFLAT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PINCHFLAT_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `PINCHFLAT_CONTAINER_NAME` |  | Container name |
| `PINCHFLAT_DOCKER_TAG` |  | Docker image tag/version |
| `PINCHFLAT_HOST_NAME` |  | Pinchflat host name |
| `PINCHFLAT_MEM_LIMIT` |  | Pinchflat mem limit |
| `PINCHFLAT_RESTART` |  | Container restart policy |
| `PINCHFLAT_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `PINCHFLAT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/pinchflat:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./media/downloads:/downloads` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${PINCHFLAT_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.pinchflat.entrypoints=websecure`
- `traefik.http.routers.pinchflat.middlewares=default-headers@file`
- `traefik.http.routers.pinchflat.rule=Host(`${PINCHFLAT_HOST_NAME:-pinchflat}.${HOST_DOMAIN}`)`
- `traefik.http.services.pinchflat.loadbalancer.server.port=8945`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PINCHFLAT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${PINCHFLAT_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${PINCHFLAT_HOST_NAME:-pinchflat}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pinchflat

# Configure environment variables (if needed)
make scaffold pinchflat

# Start the service
make up
```
