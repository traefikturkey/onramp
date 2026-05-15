# Redis

> In-memory data structure store

## Links
- [Official Repository](https://github.com/redis/redis)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/redis.yml)

## Docker Images
- `redis:${REDIS_DOCKER_TAG:-alpine}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `REDIS_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `REDIS_CONTAINER_NAME` |  | Container name |
| `REDIS_DOCKER_TAG` |  | Docker image tag/version |
| `REDIS_HOST_NAME` |  | Redis host name |
| `REDIS_NETWORK` |  | Redis network |
| `REDIS_PORT` |  | Service port number |
| `REDIS_RESTART` |  | Container restart policy |
| `REDIS_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `REDIS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${REDIS_PORT:-6379}:6379`

### Volumes
- `/etc/redis:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `${REDIS_NETWORK:-traefik}`

### Labels
**Traefik Configuration:**
- `traefik.enable=${REDIS_TRAEFIK_ENABLED:-false}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${REDIS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${REDIS_AUTOHEAL:-true}`
- `joyride.host.name=${REDIS_HOST_NAME:-redis}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable redis

# Configure environment variables (if needed)
make scaffold redis

# Start the service
make up
```
