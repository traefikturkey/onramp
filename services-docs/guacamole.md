# Guacamole

> A clientless remote desktop gateway.

## Links
- [Official Repository](https://github.com/abesnier/docker-guacamole)
- [Docker Image](https://hub.docker.com/r/abesnier/guacamole)
- [Official Documentation](https://guacamole.apache.org/doc/gug/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/guacamole.yml)

## Docker Images
- `abesnier/guacamole:${GUACAMOLE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GUACAMOLE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `GUACAMOLE_CONTAINER_NAME` |  | Container name |
| `GUACAMOLE_DOCKER_TAG` |  | Docker image tag/version |
| `GUACAMOLE_EXTENSIONS` |  | Guacamole extensions |
| `GUACAMOLE_MEM_LIMIT` |  | Guacamole mem limit |
| `GUACAMOLE_RESTART` |  | Container restart policy |
| `GUACAMOLE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `GUACAMOLE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/guacamole:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${GUACAMOLE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.guacamole.entrypoints=websecure`
- `traefik.http.routers.guacamole.rule=Host(`${GUACAMOLE_CONTAINER_NAME:-guacamole}.${HOST_DOMAIN}`)`
- `traefik.http.services.guacamole.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GUACAMOLE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${GUACAMOLE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${GUACAMOLE_CONTAINER_NAME:-guacamole}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable guacamole

# Configure environment variables (if needed)
make scaffold guacamole

# Start the service
make up
```
