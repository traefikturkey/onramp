# Homarr

> Home automation and remote control system

## Links
- [Official Repository](https://github.com/ajnart/homarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/homarr.yml)

## Docker Images
- `ghcr.io/ajnart/homarr:${HOMARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOMARR_CONTAINER_NAME` |  | Container name |
| `HOMARR_DOCKER_TAG` |  | Docker image tag/version |
| `HOMARR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/homarr/configs:/app/data/configs` - Configuration files
- `./etc/homarr/icons:/app/public/icons` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.homarr.entrypoints=websecure`
- `traefik.http.routers.homarr.rule=Host(`${HOMARR_CONTAINER_NAME:-homarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.homarr.loadbalancer.server.port=7575`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HOMARR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${HOMARR_CONTAINER_NAME:-homarr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable homarr

# Configure environment variables (if needed)
make scaffold homarr

# Start the service
make up
```
