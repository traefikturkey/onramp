# Tasktrove

> TaskTrove is a modern Todo Manager that is fully self-hostable.

## Links
- [Official Repository](https://github.com/dohsimpson/TaskTrove)
- [Official Documentation](https://docs.tasktrove.io)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/tasktrove.yml)

## Docker Images
- `ghcr.io/dohsimpson/tasktrove:${TASKTROVE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TASKTROVE_AUTH_SECRET` |  | Tasktrove auth secret |
| `TASKTROVE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `TASKTROVE_CONTAINER_NAME` |  | Container name |
| `TASKTROVE_DOCKER_TAG` |  | Docker image tag/version |
| `TASKTROVE_HOST_NAME` |  | Tasktrove host name |
| `TASKTROVE_MEM_LIMIT` |  | Tasktrove mem limit |
| `TASKTROVE_RESTART` |  | Container restart policy |
| `TASKTROVE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `TASKTROVE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/tasktrove:/app/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${TASKTROVE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.tasktrove.entrypoints=websecure`
- `traefik.http.routers.tasktrove.rule=Host(`${TASKTROVE_HOST_NAME:-tasktrove}.${HOST_DOMAIN}`)`
- `traefik.http.services.tasktrove.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TASKTROVE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${TASKTROVE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${TASKTROVE_HOST_NAME:-tasktrove}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable tasktrove

# Configure environment variables (if needed)
make scaffold tasktrove

# Start the service
make up
```
