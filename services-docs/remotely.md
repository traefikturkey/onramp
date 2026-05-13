# Remotely

> Remote desktop and support tool

## Links
- [Official Repository](https://github.com/immense/Remotely)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/remotely.yml)

## Docker Images
- `immybot/remotely:${REMOTELY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `REMOTELY_CONTAINER_NAME` |  | Container name |
| `REMOTELY_DOCKER_TAG` |  | Docker image tag/version |
| `REMOTELY_RESTART` |  | Container restart policy |
| `REMOTELY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/remotely:/app/AppData` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.remotely.entrypoints=websecure`
- `traefik.http.routers.remotely.middlewares=default-headers@file`
- `traefik.http.routers.remotely.rule=Host(`${REMOTELY_CONTAINER_NAME:-remotely}.${HOST_DOMAIN}`)`
- `traefik.http.services.remotely.loadbalancer.server.port=8080`
- `traefik.http.services.remotely.loadbalancer.server.scheme=http`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${REMOTELY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${REMOTELY_CONTAINER_NAME:-remotely}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable remotely

# Configure environment variables (if needed)
make scaffold remotely

# Start the service
make up
```
