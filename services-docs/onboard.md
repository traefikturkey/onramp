# Onboard

> An RSS and Bookmarks Dashboard

## Links
- [Official Repository](https://github.com/traefikturkey/onboard)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/onboard.yml)

## Docker Images
- `ghcr.io/traefikturkey/onboard:${ONBOARD_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OLLAMA_URL` |  | Ollama url |
| `ONBOARD_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `ONBOARD_CONTAINER_NAME` | onboard | Container name |
| `ONBOARD_DOCKER_TAG` | latest | Docker image tag/version |
| `ONBOARD_MEM_LIMIT` | 1g | Onboard mem limit |
| `ONBOARD_PAGE_TIMEOUT` | 600 | Onboard page timeout |
| `ONBOARD_RESTART` | unless-stopped | Container restart policy |
| `ONBOARD_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `ONBOARD_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/onboard:/srv/app/configs` - Volume mount
- `./etc/onboard/cache:/srv/app/.working/cache` - Volume mount
- `./etc/onboard/icons:/srv/app/static/assets/icons` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${ONBOARD_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.onboard.entrypoints=websecure`
- `traefik.http.routers.onboard.rule=Host(`${ONBOARD_CONTAINER_NAME:-onboard}.${HOST_DOMAIN}`)`
- `traefik.http.services.onboard.loadbalancer.server.port=9830`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ONBOARD_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${ONBOARD_AUTOHEAL:-true}`
- `joyride.host.name=${ONBOARD_CONTAINER_NAME:-onboard}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable onboard

# Configure environment variables (if needed)
make scaffold onboard

# Start the service
make up
```
