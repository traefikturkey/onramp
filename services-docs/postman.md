# Postman

> Hoppscotch - Open-source API development ecosystem (Postman alternative)

## Links
- [Official Repository](https://github.com/hoppscotch/hoppscotch)
- [Official Documentation](https://docs.hoppscotch.io/documentation/self-host/community-edition/install-and-build)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/postman.yml)

## Docker Images
- `hoppscotch/hoppscotch:${POSTMAN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `POSTMAN_CONTAINER_NAME` |  | Container name |
| `POSTMAN_DOCKER_TAG` |  | Docker image tag/version |
| `POSTMAN_RESTART` |  | Container restart policy |
| `POSTMAN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.postman.entrypoints=websecure`
- `traefik.http.routers.postman.rule=Host(`${POSTMAN_CONTAINER_NAME:-hoppscotch}.${HOST_DOMAIN}`)`
- `traefik.http.services.postman.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${POSTMAN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${POSTMAN_CONTAINER_NAME:-hoppscotch}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable postman

# Configure environment variables (if needed)
make scaffold postman

# Start the service
make up
```
