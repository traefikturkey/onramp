# Bazarr

> Manages subtitles for media content

## Links
- [Official Repository](https://github.com/linuxserver/docker-bazarr)
- [Docker Image](https://hub.docker.com/r/linuxserver/bazarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/bazarr.yml)

## Docker Images
- `lscr.io/linuxserver/bazarr:${BAZARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BAZARR_CONTAINER_NAME` |  | Container name |
| `BAZARR_DOCKER_TAG` |  | Docker image tag/version |
| `BAZARR_MOVIES_VOLUME` |  | Bazarr movies volume |
| `BAZARR_SHOWS_VOLUME` |  | Bazarr shows volume |
| `BAZARR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `6767:6767`

### Volumes
- `./etc/bazarr:/config` - Volume mount
- `${BAZARR_MOVIES_VOLUME:-./media/movies}` - Volume mount
- `${BAZARR_SHOWS_VOLUME:-./media/shows}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.bazarr.entrypoints=websecure`
- `traefik.http.routers.bazarr.rule=Host(`${BAZARR_CONTAINER_NAME:-bazarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.bazarr.loadbalancer.server.port=6767`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BAZARR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${BAZARR_CONTAINER_NAME:-bazarr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable bazarr

# Configure environment variables (if needed)
make scaffold bazarr

# Start the service
make up
```
