# Lazylibrarian

> LazyLibrarian is a SickBeard, CouchPotato, Headphones-like application for ebooks, audiobooks and magazines

## Links
- [Official Documentation](https://lazylibrarian.gitlab.io/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/lazylibrarian.yml)

## Docker Images
- `lscr.io/linuxserver/lazylibrarian:${LAZYLIBRARIAN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `LAZYLIBRARIAN_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `LAZYLIBRARIAN_CONTAINER_NAME` |  | Container name |
| `LAZYLIBRARIAN_DOCKER_TAG` |  | Docker image tag/version |
| `LAZYLIBRARIAN_HOST_NAME` |  | Lazylibrarian host name |
| `LAZYLIBRARIAN_MEM_LIMIT` |  | Lazylibrarian mem limit |
| `LAZYLIBRARIAN_RESTART` |  | Container restart policy |
| `LAZYLIBRARIAN_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `LAZYLIBRARIAN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `MEDIA_BOOKS_VOLUME` |  | Media books volume |
| `MEDIA_DOWNLOADS_VOLUME` |  | Media downloads volume |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/lazylibrarian:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `${MEDIA_BOOKS_VOLUME:-./media/books}` - Volume mount
- `${MEDIA_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${LAZYLIBRARIAN_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.lazylibrarian.entrypoints=websecure`
- `traefik.http.routers.lazylibrarian.rule=Host(`${LAZYLIBRARIAN_HOST_NAME:-lazylibrarian}.${HOST_DOMAIN}`)`
- `traefik.http.services.lazylibrarian.loadbalancer.server.port=5299`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LAZYLIBRARIAN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${LAZYLIBRARIAN_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${LAZYLIBRARIAN_HOST_NAME:-lazylibrarian}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable lazylibrarian

# Configure environment variables (if needed)
make scaffold lazylibrarian

# Start the service
make up
```
