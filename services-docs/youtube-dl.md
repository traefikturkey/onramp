# Youtube Dl

> Web UI for youtube-dl to download videos from youtube and other sites

## Links
- [Official Repository](https://github.com/nbr23/youtube-dl-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/youtube-dl.yml)

## Docker Images
- `nbr23/youtube-dl-server:${YOUTUBE_DL_DOCKER_TAG:-yt-dlp}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `YOUTUBE_DL_CONTAINER_NAME` |  | Container name |
| `YOUTUBE_DL_DOCKER_TAG` |  | Docker image tag/version |
| `YOUTUBE_DL_DOWNLOAD_PATH` |  | Youtube dl download path |
| `YOUTUBE_DL_RESTART` |  | Container restart policy |
| `YOUTUBE_DL_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/youtube-dl:/youtube-dl` - Volume mount
- `${YOUTUBE_DL_DOWNLOAD_PATH:-./etc/youtube-dl/downloads}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.youtube-dl.entrypoints=websecure`
- `traefik.http.routers.youtube-dl.rule=Host(`${YOUTUBE_DL_CONTAINER_NAME:-youtube-dl}.${HOST_DOMAIN}`)`
- `traefik.http.services.youtube-dl.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${YOUTUBE_DL_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${YOUTUBE_DL_CONTAINER_NAME:-youtube-dl}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable youtube-dl

# Configure environment variables (if needed)
make scaffold youtube-dl

# Start the service
make up
```
