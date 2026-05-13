# Tdarr

> Media optimization and conversion tool

## Links
- [Official Documentation](https://docs.tdarr.io/docs/installation/docker/run-compose)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/tdarr.yml)

## Docker Images
- `ghcr.io/haveagitgat/tdarr:${TDARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TDARR_CONTAINER_NAME` |  | Container name |
| `TDARR_DOCKER_TAG` |  | Docker image tag/version |
| `TDARR_INTERNAL_NODE` |  | Tdarr internal node |
| `TDARR_MEDIA_PATH` |  | Tdarr media path |
| `TDARR_MEDIA_VOLUME` |  | Tdarr media volume |
| `TDARR_NODE_ID` |  | Tdarr node id |
| `TDARR_RESTART` |  | Container restart policy |
| `TDARR_SERVER_PORT` |  | Service port number |
| `TDARR_TEMP_PATH` |  | Tdarr temp path |
| `TDARR_TEMP_VOLUME` |  | Tdarr temp volume |
| `TDARR_UMASK` |  | Tdarr umask |
| `TDARR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TDARR_WEB_PORT` |  | Service port number |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${TDARR_SERVER_PORT:-8266}:${TDARR_SERVER_PORT:-8266}`

### Volumes
- `./etc/tdarr/server:/app/server` - Volume mount
- `./etc/tdarr/config:/app/configs` - Configuration files
- `${TDARR_MEDIA_VOLUME:-./media}` - Volume mount
- `${TDARR_TEMP_VOLUME:-./media/tdarr-temp}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.tdarr.entrypoints=websecure`
- `traefik.http.routers.tdarr.rule=Host(`${TDARR_CONTAINER_NAME:-tdarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.tdarr.loadbalancer.server.port=${TDARR_WEB_PORT:-8265}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TDARR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${TDARR_CONTAINER_NAME:-tdarr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable tdarr

# Configure environment variables (if needed)
make scaffold tdarr

# Start the service
make up
```
