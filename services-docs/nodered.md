# Nodered

> Flow-based development tool for visual programming

## Links
- [Official Repository](https://github.com//node-red/node-red-docker)
- [Docker Image](https://hub.docker.com/r/nodered/node-red/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nodered.yml)

## Docker Images
- `ghcr.io/node-red/node-red:${NODERED_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NODERED_DOCKER_TAG` |  | Docker image tag/version |
| `NODERED_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/nodered:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.nodered.entrypoints=websecure`
- `traefik.http.routers.nodered.rule=Host(`nodered.${HOST_DOMAIN}`)`
- `traefik.http.services.nodered.loadbalancer.server.port=1880`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NODERED_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=nodered.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable nodered

# Configure environment variables (if needed)
make scaffold nodered

# Start the service
make up
```
