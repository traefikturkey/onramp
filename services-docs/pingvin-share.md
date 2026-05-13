# Pingvin Share

> File-sharing platform

## Links
- [Official Repository](https://github.com/stautonico/pingvin-share)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pingvin-share.yml)

## Docker Images
- `ghcr.io/stonith404/pingvin-share:${PINGVIN_SHARE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PINGVIN_MEDIA_VOLUME` |  | Pingvin media volume |
| `PINGVIN_SHARE_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `PINGVIN_SHARE_CONTAINER_NAME` |  | Container name |
| `PINGVIN_SHARE_DOCKER_TAG` |  | Docker image tag/version |
| `PINGVIN_SHARE_RESTART` |  | Container restart policy |
| `PINGVIN_SHARE_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `PINGVIN_SHARE_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/pingvin-share:/opt/app/backend/data` - Volume mount
- `${PINGVIN_MEDIA_VOLUME:-./media/pingvin}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${PINGVIN_SHARE_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.pingvin.entrypoints=websecure`
- `traefik.http.routers.pingvin.rule=Host(`${PINGVIN_SHARE_CONTAINER_NAME:-pingvin}.${HOST_DOMAIN}`)`
- `traefik.http.services.pingvin.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PINGVIN_SHARE_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${PINGVIN_SHARE_AUTOHEAL:-true}`
- `joyride.host.name=${PINGVIN_SHARE_CONTAINER_NAME:-pingvin}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pingvin-share

# Configure environment variables (if needed)
make scaffold pingvin-share

# Start the service
make up
```
