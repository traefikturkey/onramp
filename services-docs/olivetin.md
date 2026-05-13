# Olivetin

> Access predefined shell commands from a web interface.

## Links
- [Official Repository](https://github.com/OliveTin/OliveTin)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/olivetin.yml)

## Docker Images
- `ghcr.io/olivetin/olivetin:${OLIVETIN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OLIVETIN_CONTAINER_NAME` |  | Container name |
| `OLIVETIN_DOCKER_TAG` |  | Docker image tag/version |
| `OLIVETIN_HOST_NAME` |  | Olivetin host name |
| `OLIVETIN_RESTART` |  | Container restart policy |
| `OLIVETIN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/olivetin:/config` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.olivetin.entrypoints=websecure`
- `traefik.http.routers.olivetin.rule=Host(`${OLIVETIN_HOST_NAME:-olivetin}.${HOST_DOMAIN}`)`
- `traefik.http.services.olivetin.loadbalancer.server.port=1337`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OLIVETIN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${OLIVETIN_HOST_NAME:-olivetin}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable olivetin

# Configure environment variables (if needed)
make scaffold olivetin

# Start the service
make up
```
