# Sd Web

> stable diffusion web interface for ai images

## Links
- [Official Repository](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/sd-web.yml)

## Docker Images
- `ghcr.io/traefikturkey/sd-webui-docker:${SD_WEB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SD_WEB_CONTAINER_NAME` |  | Container name |
| `SD_WEB_DOCKER_TAG` |  | Docker image tag/version |
| `SD_WEB_RESTART` |  | Container restart policy |
| `SD_WEB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/sd-web:/data` - Volume mount
- `./media/sd-web:/output` - Volume mount
- `./media/models:/models` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.sd-web.entrypoints=websecure`
- `traefik.http.routers.sd-web.rule=Host(`${SD_WEB_CONTAINER_NAME:-sd-web}.${HOST_DOMAIN}`)`
- `traefik.http.services.sd-web.loadbalancer.server.port=7860`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SD_WEB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SD_WEB_CONTAINER_NAME:-sd-web}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable sd-web

# Configure environment variables (if needed)
make scaffold sd-web

# Start the service
make up
```
