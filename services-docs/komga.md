# Komga

> Web-based comic book server

## Links
- [Official Documentation](https://komga.org/docs/installation/docker/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/komga.yml)

## Docker Images
- `ghcr.io/gotson/komga:${KOMGA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KOMGA_CONTAINER_NAME` |  | Container name |
| `KOMGA_DOCKER_TAG` |  | Docker image tag/version |
| `KOMGA_RESTART` |  | Container restart policy |
| `KOMGA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `MEDIA_COMICS_VOLUME` |  | Media comics volume |
| `MEDIA_MANGA_VOLUME` |  | Media manga volume |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/komga:/config` - Volume mount
- `${MEDIA_MANGA_VOLUME:-./media/manga}` - Volume mount
- `${MEDIA_COMICS_VOLUME:-./media/comics}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.komga.entrypoints=websecure`
- `traefik.http.routers.komga.rule=Host(`${KOMGA_CONTAINER_NAME:-komga}.${HOST_DOMAIN}`)`
- `traefik.http.services.komga.loadbalancer.server.port=25600`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KOMGA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${KOMGA_CONTAINER_NAME:-komga}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable komga

# Configure environment variables (if needed)
make scaffold komga

# Start the service
make up
```
