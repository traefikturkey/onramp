# Readarr

> Manages ebook collections and downloads

## Links
- [Official Repository](https://github.com/Readarr/Readarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/readarr.yml)

## Docker Images
- `lscr.io/linuxserver/readarr:${READARR_DOCKER_TAG:-nightly}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MEDIA_BOOKS_VOLUME` | ./media/books | Media books volume |
| `MEDIA_DOWNLOADS_VOLUME` | ./media/downloads | Media downloads volume |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `READARR_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `READARR_CONTAINER_NAME` | readarr | Container name |
| `READARR_DOCKER_TAG` | nightly | Docker image tag/version |
| `READARR_RESTART` | unless-stopped | Container restart policy |
| `READARR_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `READARR_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `8787:8787`

### Volumes
- `./etc/readarr:/config` - Volume mount
- `${MEDIA_BOOKS_VOLUME:-./media/books}` - Volume mount
- `${MEDIA_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount
- `/dev/rtc:/dev/rtc` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${READARR_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.readarr.entrypoints=websecure`
- `traefik.http.routers.readarr.rule=Host(`${READARR_CONTAINER_NAME:-readarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.readarr.loadbalancer.server.port=8787`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${READARR_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${READARR_AUTOHEAL:-true}`
- `joyride.host.name=${READARR_CONTAINER_NAME:-readarr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable readarr

# Configure environment variables (if needed)
make scaffold readarr

# Start the service
make up
```
