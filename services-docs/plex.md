# Plex

> Media server for streaming movies, tv shows, and music

## Links
- [Official Repository](https://github.com/plexinc/pms-docker)
- [Official Documentation](https://www.plex.tv/claim)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/plex.yml)

## Docker Images
- `plexinc/pms-docker:${PLEX_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PLEX_ALLOWED_NETWORKS` | 192.168.0.0/16 | Plex allowed networks |
| `PLEX_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `PLEX_CLAIM` | ${PLEX_CLAIM:-} | Plex claim |
| `PLEX_CONTAINER_NAME` | plex | Container name |
| `PLEX_DOCKER_TAG` | latest | Docker image tag/version |
| `PLEX_MEDIA_PATH` | /data | Plex media path |
| `PLEX_MEDIA_VOLUME` | ./media | Plex media volume |
| `PLEX_RESTART` | unless-stopped | Container restart policy |
| `PLEX_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `PLEX_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `3005:3005/tcp`
- `8324:8324/tcp`
- `32469:32469/tcp`
- `1900:1900/udp`
- `32410:32410/udp`
- `32412:32412/udp`
- `32413:32413/udp`
- `32414:32414/udp`

### Volumes
- `./etc/plex:/config` - Volume mount
- `${PLEX_MEDIA_VOLUME:-./media}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${PLEX_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.plex.entrypoints=websecure`
- `traefik.http.routers.plex.rule=Host(`${PLEX_CONTAINER_NAME:-plex}.${HOST_DOMAIN}`)`
- `traefik.http.services.plex.loadbalancer.server.port=32400`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PLEX_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${PLEX_AUTOHEAL:-true}`
- `joyride.host.name=${PLEX_CONTAINER_NAME:-plex}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable plex

# Configure environment variables (if needed)
make scaffold plex

# Start the service
make up
```
