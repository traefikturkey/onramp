# Scrypted

> Home automation platform

## Links
- [Official Repository](https://github.com/koush/scrypted)
- [Official Documentation](https://docs.technotim.live/posts/scrypted-home-hub/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/scrypted.yml)

## Docker Images
- `ghcr.io/koush/scrypted:${SCRYPTED_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SCRYPTED_CONTAINER_NAME` |  | Container name |
| `SCRYPTED_DOCKER_TAG` |  | Docker image tag/version |
| `SCRYPTED_RESTART` |  | Container restart policy |
| `SCRYPTED_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `SCRYPTED_WEBHOOK_UPDATE` |  | Scrypted webhook update |
| `SCRYPTED_WEBHOOK_UPDATE_AUTHORIZATION` |  | Scrypted webhook update authorization |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/scrypted:/server/volume` - Volume mount
- `./media/videos/scrypted:/media/external` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.scrypted.entrypoints=websecure`
- `traefik.http.routers.scrypted.rule=Host(`${SCRYPTED_CONTAINER_NAME:-scrypted}.${HOST_DOMAIN}`)`
- `traefik.http.services.scrypted.loadbalancer.server.port=10443`
- `traefik.http.services.scrypted.loadbalancer.server.scheme=https`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SCRYPTED_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SCRYPTED_CONTAINER_NAME:-scrypted}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable scrypted

# Configure environment variables (if needed)
make scaffold scrypted

# Start the service
make up
```
