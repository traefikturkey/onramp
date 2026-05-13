# Pwndrop

> Self-hosted file-sharing platform

## Links
- [Official Repository](https://github.com/kgretzky/pwndrop)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pwndrop.yml)

## Docker Images
- `lscr.io/linuxserver/pwndrop:${PWNDROP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `PWNDROP_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `PWNDROP_CONTAINER_NAME` |  | Container name |
| `PWNDROP_DOCKER_TAG` |  | Docker image tag/version |
| `PWNDROP_SECRET_PATH` |  | Pwndrop secret path |
| `PWNDROP_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `PWNDROP_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/pwndrop:/config` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${PWNDROP_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.pwndrop.entrypoints=websecure`
- `traefik.http.routers.pwndrop.rule=Host(`${PWNDROP_CONTAINER_NAME:-pwndrop}.${HOST_DOMAIN}`)`
- `traefik.http.services.pwndrop.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PWNDROP_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${PWNDROP_AUTOHEAL:-true}`
- `joyride.host.name=${PWNDROP_CONTAINER_NAME:-pwndrop}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pwndrop

# Configure environment variables (if needed)
make scaffold pwndrop

# Start the service
make up
```
