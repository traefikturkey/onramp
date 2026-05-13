# Headphones

> Headphones is an automated music downloader for NZB and Torrent, written in Python

## Links
- [Official Repository](https://github.com/rembo10/headphones)
- [Docker Image](https://hub.docker.com/r/linuxserver/headphones)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/headphones.yml)

## Docker Images
- `alonlivne/headphones:${HEADPHONES_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEADPHONES_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `HEADPHONES_CONTAINER_NAME` |  | Container name |
| `HEADPHONES_DOCKER_TAG` |  | Docker image tag/version |
| `HEADPHONES_DOWNLOADS_VOLUME` |  | Headphones downloads volume |
| `HEADPHONES_HOST_NAME` |  | Headphones host name |
| `HEADPHONES_MUSIC_VOLUME` |  | Headphones music volume |
| `HEADPHONES_RESTART` |  | Container restart policy |
| `HEADPHONES_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `HEADPHONES_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/headphones:/config` - Volume mount
- `${HEADPHONES_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount
- `${HEADPHONES_MUSIC_VOLUME:-./media/music}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${HEADPHONES_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.headphones.entrypoints=websecure`
- `traefik.http.routers.headphones.rule=Host(`${HEADPHONES_HOST_NAME:-headphones}.${HOST_DOMAIN}`)`
- `traefik.http.services.headphones.loadbalancer.server.port=8181`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HEADPHONES_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${HEADPHONES_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${HEADPHONES_HOST_NAME:-headphones}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable headphones

# Configure environment variables (if needed)
make scaffold headphones

# Start the service
make up
```
