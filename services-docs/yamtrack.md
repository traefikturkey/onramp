# Yamtrack

> A self hosted media tracker.

## Links
- [Official Repository](https://github.com/FuzzyGrim/Yamtrack)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/yamtrack.yml)

## Docker Images
- `ghcr.io/fuzzygrim/yamtrack:${YAMTRACK_DOCKER_TAG:-latest}`
- `redis:7-alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `YAMTRACK_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `YAMTRACK_CONTAINER_NAME` |  | Container name |
| `YAMTRACK_DOCKER_TAG` |  | Docker image tag/version |
| `YAMTRACK_HOST_NAME` |  | Yamtrack host name |
| `YAMTRACK_MEM_LIMIT` |  | Yamtrack mem limit |
| `YAMTRACK_RESTART` |  | Container restart policy |
| `YAMTRACK_SECRET` |  | Yamtrack secret |
| `YAMTRACK_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `YAMTRACK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/yamtrack/db:/yamtrack/db` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/yamtrack/redis:/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${YAMTRACK_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.yamtrack.entrypoints=websecure`
- `traefik.http.routers.yamtrack.rule=Host(`${YAMTRACK_HOST_NAME:-yamtrack}.${HOST_DOMAIN}`)`
- `traefik.http.services.yamtrack.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${YAMTRACK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${YAMTRACK_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${YAMTRACK_HOST_NAME:-yamtrack}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `yamtrack-redis`

## Quick Start

```bash
# Enable the service
make enable yamtrack

# Configure environment variables (if needed)
make scaffold yamtrack

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires yamtrack-redis to be running
