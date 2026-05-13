# Homer

> Self-hosted bookmark manager

## Links
- [Official Repository](https://github.com/bastienwirtz/homer)
- [Docker Image](https://hub.docker.com/r/b4bz/homer)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/homer.yml)

## Docker Images
- `b4bz/homer:${HOMER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOMER_ASSETS_DIR` |  | Homer assets dir |
| `HOMER_CONTAINER_NAME` |  | Container name |
| `HOMER_DOCKER_TAG` |  | Docker image tag/version |
| `HOMER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${HOMER_ASSETS_DIR:-./etc/homer}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.homer.entrypoints=websecure`
- `traefik.http.routers.homer.rule=Host(`${HOMER_CONTAINER_NAME:-homer}.${HOST_DOMAIN}`)`
- `traefik.http.services.homer.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HOMER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${HOMER_CONTAINER_NAME:-homer}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable homer

# Configure environment variables (if needed)
make scaffold homer

# Start the service
make up
```
