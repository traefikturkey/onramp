# Flame

> homepage/dashboard for docker containers and services

## Links
- [Official Repository](https://github.com/pawelmalak/flame)
- [Docker Image](https://hub.docker.com/r/pawelmalak/flame)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/flame.yml)

## Docker Images
- `pawelmalak/flame:${FLAME_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLAME_CONTAINER_NAME` |  | Container name |
| `FLAME_DOCKER_TAG` |  | Docker image tag/version |
| `FLAME_PASSWORD` |  | Service password |
| `FLAME_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/flame:/app/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.flame.entrypoints=websecure`
- `traefik.http.routers.flame.rule=Host(`${FLAME_CONTAINER_NAME:-flame}.${HOST_DOMAIN}`)`
- `traefik.http.services.flame.loadbalancer.server.port=5005`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FLAME_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FLAME_CONTAINER_NAME:-flame}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable flame

# Configure environment variables (if needed)
make scaffold flame

# Start the service
make up
```
