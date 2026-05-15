# Navidrome

> A music collection server and web client for streaming your music

## Links
- [Official Repository](https://github.com/navidrome/navidrome/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/navidrome.yml)

## Docker Images
- `ghcr.io/navidrome/navidrome:${NAVIDROME_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NAVIDROME_CONTAINER_NAME` |  | Container name |
| `NAVIDROME_DOCKER_TAG` |  | Docker image tag/version |
| `NAVIDROME_MUSIC_PATH` |  | Navidrome music path |
| `NAVIDROME_MUSIC_VOLUME` |  | Navidrome music volume |
| `NAVIDROME_RESTART` |  | Container restart policy |
| `NAVIDROME_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `4533:4533`

### Volumes
- `/etc/navidrome:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `${NAVIDROME_MUSIC_VOLUME:-./media/music}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.navidrome.entrypoints=websecure`
- `traefik.http.routers.navidrome.rule=Host(`${NAVIDROME_CONTAINER_NAME:-navidrome}.${HOST_DOMAIN}`)`
- `traefik.http.services.navidrome.loadbalancer.server.port=4533`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NAVIDROME_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${NAVIDROME_CONTAINER_NAME:-navidrome}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable navidrome

# Configure environment variables (if needed)
make scaffold navidrome

# Start the service
make up
```
