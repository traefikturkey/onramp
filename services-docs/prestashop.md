# Prestashop

> E-commerce platform

## Links
- [Official Repository](https://github.com/PrestaShop/PrestaShop)
- [Docker Image](https://hub.docker.com/r/prestashop/prestashop/)
- [Official Documentation](https://www.prestashop.com/en)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prestashop.yml)

## Docker Images
- `prestashop/prestashop:${PRESTASHOP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PRESTASHOP_CONTAINER_NAME` |  | Container name |
| `PRESTASHOP_DOCKER_TAG` |  | Docker image tag/version |
| `PRESTASHOP_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/prestashop:/var/www/html/` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.prestashop.entrypoints=websecure`
- `traefik.http.routers.prestashop.rule=Host(`${PRESTASHOP_CONTAINER_NAME:-prestashop}.${HOST_DOMAIN}`)`
- `traefik.http.services.prestashop.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PRESTASHOP_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PRESTASHOP_CONTAINER_NAME:-prestashop}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable prestashop

# Configure environment variables (if needed)
make scaffold prestashop

# Start the service
make up
```
