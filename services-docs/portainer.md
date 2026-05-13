# Portainer

> Lightweight container management ui

## Links
- [Official Repository](https://github.com/portainer/portainer)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/portainer.yml)

## Docker Images
- `portainer/portainer-${PORTAINER_VERSION:-ce}:${PORTAINER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PORTAINER_CONTAINER_NAME` |  | Container name |
| `PORTAINER_DOCKER_TAG` |  | Docker image tag/version |
| `PORTAINER_LICENSE_KEY` |  | Service port number |
| `PORTAINER_VERSION` |  | Service port number |
| `PORTAINER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/portainer:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.portainer.entrypoints=websecure`
- `traefik.http.routers.portainer.rule=Host(`${PORTAINER_CONTAINER_NAME:-portainer}.${HOST_DOMAIN}`)`
- `traefik.http.services.portainer.loadbalancer.server.port=9000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PORTAINER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PORTAINER_CONTAINER_NAME:-portainer}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable portainer

# Configure environment variables (if needed)
make scaffold portainer

# Start the service
make up
```
