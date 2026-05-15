# Super Productivity

> Time and task management app

## Links
- [Official Repository](https://github.com/johannesjo/super-productivity)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/super-productivity.yml)

## Docker Images
- `johannesjo/super-productivity:${SUPER_PRODUCTIVITY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SUPER_PRODUCTIVITY_CONTAINER_NAME` |  | Container name |
| `SUPER_PRODUCTIVITY_DOCKER_TAG` |  | Docker image tag/version |
| `SUPER_PRODUCTIVITY_RESTART` |  | Container restart policy |
| `SUPER_PRODUCTIVITY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/super-productivity:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.super-productivity.entrypoints=websecure`
- `traefik.http.routers.super-productivity.rule=Host(`${SUPER_PRODUCTIVITY_CONTAINER_NAME:-super-productivity}.${HOST_DOMAIN}`)`
- `traefik.http.services.super-productivity.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SUPER_PRODUCTIVITY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SUPER_PRODUCTIVITY_CONTAINER_NAME:-super-productivity}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable super-productivity

# Configure environment variables (if needed)
make scaffold super-productivity

# Start the service
make up
```
