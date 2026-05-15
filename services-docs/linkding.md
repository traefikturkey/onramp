# Linkding

> Self-hosted bookmark manager

## Links
- [Official Repository](https://github.com/sissbruecker/linkding)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/linkding.yml)

## Docker Images
- `sissbruecker/linkding:${LINKDING_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `LD_ENABLE_AUTH_PROXY` |  | Ld enable auth proxy |
| `LD_SUPERUSER_NAME` |  | Service username |
| `LD_SUPERUSER_PASSWORD` |  | Service password |
| `LINKDING_CONTAINER_NAME` |  | Container name |
| `LINKDING_DOCKER_TAG` |  | Docker image tag/version |
| `LINKDING_RESTART` |  | Container restart policy |
| `LINKDING_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/linkding/data:/etc/linkding/data` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.linkding.entrypoints=websecure`
- `traefik.http.routers.linkding.rule=Host(`${LINKDING_CONTAINER_NAME:-linkding}.${HOST_DOMAIN}`)`
- `traefik.http.services.linkding.loadbalancer.server.port=9090`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LINKDING_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${LINKDING_CONTAINER_NAME:-linkding}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable linkding

# Configure environment variables (if needed)
make scaffold linkding

# Start the service
make up
```
