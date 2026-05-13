# Rundeck

> Job scheduler and runbook automation platform

## Links
- [Official Repository](https://github.com/rundeck/rundeck)
- [Docker Image](https://hub.docker.com/r/rundeck/rundeck)
- [Official Documentation](https://docs.rundeck.com/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/rundeck.yml)

## Docker Images
- `rundeck/rundeck:${RUNDECK_DOCKER_TAG:-5.0.1}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `RUNDECK_CONTAINER_NAME` |  | Container name |
| `RUNDECK_DOCKER_TAG` |  | Docker image tag/version |
| `RUNDECK_RESTART` |  | Container restart policy |
| `RUNDECK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/rundeck/db:/home/rundeck/server/data` - Volume mount
- `./etc/rundeck/config:/home/rundeck/server/config` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.rundeck.entrypoints=websecure`
- `traefik.http.routers.rundeck.rule=Host(`${RUNDECK_CONTAINER_NAME:-rundeck}.${HOST_DOMAIN}`)`
- `traefik.http.services.rundeck.loadbalancer.server.port=4440`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${RUNDECK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${RUNDECK_CONTAINER_NAME:-rundeck}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable rundeck

# Configure environment variables (if needed)
make scaffold rundeck

# Start the service
make up
```
