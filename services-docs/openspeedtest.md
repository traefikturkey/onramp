# Openspeedtest

> web-based speed test application

## Links
- [Official Repository](https://github.com/openspeedtest/Docker-Image)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/openspeedtest.yml)

## Docker Images
- `openspeedtest/${OPENSPEEDTEST_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OPENSPEEDTEST_CONTAINER_NAME` |  | Container name |
| `OPENSPEEDTEST_DOCKER_TAG` |  | Docker image tag/version |
| `OPENSPEEDTEST_RESTART` |  | Container restart policy |
| `OPENSPEEDTEST_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.middlewares.limit.buffering.maxRequestBodyBytes=10000000000`
- `traefik.http.routers.openspeedtest.entrypoints=websecure`
- `traefik.http.routers.openspeedtest.middlewares=limit`
- `traefik.http.routers.openspeedtest.rule=Host(`${OPENSPEEDTEST_CONTAINER_NAME:-openspeedtest}.${HOST_DOMAIN}`)`
- `traefik.http.services.openspeedtest.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OPENSPEEDTEST_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${OPENSPEEDTEST_CONTAINER_NAME:-openspeedtest}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable openspeedtest

# Configure environment variables (if needed)
make scaffold openspeedtest

# Start the service
make up
```
