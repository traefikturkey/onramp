# Photoprism

> Personal photo management software

## Links
- [Official Repository](https://github.com/photoprism/photoprism)
- [Docker Image](https://hub.docker.com/r/photoprism/photoprism)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/photoprism.yml)

## Docker Images
- `photoprism/photoprism:${PHOTOPRISM_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PHOTOPRISM_ADMIN_PASSWORD` |  | Service password |
| `PHOTOPRISM_CONTAINER_NAME` |  | Container name |
| `PHOTOPRISM_DOCKER_TAG` |  | Docker image tag/version |
| `PHOTOPRISM_MEDIA_PHOTOS` |  | Photoprism media photos |
| `PHOTOPRISM_MEDIA_VIDEOS` |  | Photoprism media videos |
| `PHOTOPRISM_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/photoprism/:/photoprism/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `${PHOTOPRISM_MEDIA_PHOTOS:-./media/photos}` - Volume mount
- `${PHOTOPRISM_MEDIA_VIDEOS:-./media/videos}` - Volume mount
- `./etc/photoprism/storage:/photoprism/storage` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.photoprism.entrypoints=websecure`
- `traefik.http.routers.photoprism.rule=Host(`${PHOTOPRISM_CONTAINER_NAME:-photoprism}.${HOST_DOMAIN}`)`
- `traefik.http.services.photoprism.loadbalancer.server.port=2342`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PHOTOPRISM_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PHOTOPRISM_CONTAINER_NAME:-photoprism}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable photoprism

# Configure environment variables (if needed)
make scaffold photoprism

# Start the service
make up
```
