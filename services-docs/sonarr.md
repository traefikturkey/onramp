# Sonarr

> Manages tv show collections and downloads

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/sonarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/sonarr.yml)

## Docker Images
- `lscr.io/linuxserver/sonarr:${SONARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MEDIA_DOWNLOADS_VOLUME` | ./media/downloads | Media downloads volume |
| `MEDIA_SHOWS_VOLUME` | ./media/shows | Media shows volume |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SONARR_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `SONARR_CONTAINER_NAME` | sonarr | Container name |
| `SONARR_DOCKER_TAG` | latest | Docker image tag/version |
| `SONARR_RESTART` | unless-stopped | Container restart policy |
| `SONARR_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `SONARR_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/sonarr:/config` - Volume mount
- `${MEDIA_SHOWS_VOLUME:-./media/shows}` - Volume mount
- `${MEDIA_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount
- `/dev/rtc:/dev/rtc` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SONARR_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.sonarr.entrypoints=websecure`
- `traefik.http.routers.sonarr.rule=Host(`${SONARR_CONTAINER_NAME:-sonarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.sonarr.loadbalancer.server.port=8989`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SONARR_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${SONARR_AUTOHEAL:-true}`
- `joyride.host.name=${SONARR_CONTAINER_NAME:-sonarr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable sonarr

# Configure environment variables (if needed)
make scaffold sonarr

# Start the service
make up
```
