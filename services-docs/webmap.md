# Webmap

> Web-based network scanner

## Links
- [Official Repository](https://github.com/SECUREFOREST/WebMap)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/webmap.yml)

## Docker Images
- `secureforest/webmap:${WEBMAP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WEBMAP_CONFIG_PATH` |  | Webmap config path |
| `WEBMAP_CONTAINER_NAME` |  | Container name |
| `WEBMAP_DOCKER_TAG` |  | Docker image tag/version |
| `WEBMAP_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `${WEBMAP_CONFIG_PATH:-./etc/webmap}` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.webmap.entrypoints=websecure`
- `traefik.http.routers.webmap.rule=Host(`${WEBMAP_CONTAINER_NAME:-webmap}.${HOST_DOMAIN}`)`
- `traefik.http.services.webmap.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WEBMAP_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WEBMAP_CONTAINER_NAME:-webmap}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable webmap

# Configure environment variables (if needed)
make scaffold webmap

# Start the service
make up
```
