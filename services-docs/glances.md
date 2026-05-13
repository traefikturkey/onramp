# Glances

> System monitoring tool

## Links
- [Official Repository](https://github.com/nicolargo/glances)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/glances.yml)

## Docker Images
- `nicolargo/glances:${GLANCES_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GLANCES_CONTAINER_NAME` |  | Container name |
| `GLANCES_DOCKER_TAG` |  | Docker image tag/version |
| `GLANCES_RESTART` |  | Container restart policy |
| `GLANCES_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `./etc/glances:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.glances.entrypoints=websecure`
- `traefik.http.routers.glances.rule=Host(`${GLANCES_CONTAINER_NAME:-glances}.${HOST_DOMAIN}`)`
- `traefik.http.services.glances.loadbalancer.server.port=61208`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GLANCES_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GLANCES_CONTAINER_NAME:-glances}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable glances

# Configure environment variables (if needed)
make scaffold glances

# Start the service
make up
```
