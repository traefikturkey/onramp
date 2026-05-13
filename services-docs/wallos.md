# Wallos

> Open-Source Personal Subscription Tracker

## Links
- [Official Repository](https://github.com/ellite/Wallos)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wallos.yml)

## Docker Images
- `bellamy/wallos:${WALLOS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WALLOS_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `WALLOS_CONTAINER_NAME` |  | Container name |
| `WALLOS_DOCKER_TAG` |  | Docker image tag/version |
| `WALLOS_MEM_LIMIT` |  | Wallos mem limit |
| `WALLOS_RESTART` |  | Container restart policy |
| `WALLOS_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `WALLOS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/wallos/db:/var/www/html/db` - Volume mount
- `./etc/wallos/db/logos:/var/www/html/images/uploads/logos` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${WALLOS_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.wallos.entrypoints=websecure`
- `traefik.http.routers.wallos.rule=Host(`${WALLOS_CONTAINER_NAME:-wallos}.${HOST_DOMAIN}`)`
- `traefik.http.services.wallos.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WALLOS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${WALLOS_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${WALLOS_CONTAINER_NAME:-wallos}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wallos

# Configure environment variables (if needed)
make scaffold wallos

# Start the service
make up
```
