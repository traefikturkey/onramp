# Dashy

> Customizable dashboard for displaying information

## Links
- [Official Repository](https://github.com/Lissy93/dashy)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dashy.yml)

## Docker Images
- `ghcr.io/lissy93/dashy:${DASHY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DASHY_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `DASHY_CONTAINER_NAME` |  | Container name |
| `DASHY_DOCKER_TAG` |  | Docker image tag/version |
| `DASHY_RESTART` |  | Container restart policy |
| `DASHY_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `DASHY_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/dashy/dashy-config.yml:/app/public/conf.yml` - Configuration files
- `./media/assets/dashy-icons:/app/public/item-icons` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DASHY_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.dashy.entrypoints=websecure`
- `traefik.http.routers.dashy.rule=Host(`${DASHY_CONTAINER_NAME:-dashy}.${HOST_DOMAIN}`)`
- `traefik.http.services.dashy.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DASHY_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${DASHY_AUTOHEAL:-true}`
- `joyride.host.name=${DASHY_CONTAINER_NAME:-dashy}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable dashy

# Configure environment variables (if needed)
make scaffold dashy

# Start the service
make up
```
