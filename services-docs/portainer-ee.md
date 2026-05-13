# Portainer Ee

> Commercial version of portainer, a container management tool

## Links
- [Official Repository](https://github.com/portainer/portainer)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/portainer-ee.yml)

## Docker Images
- `portainer/portainer-ee:${PORTAINER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PORTAINER_DOCKER_TAG` |  | Docker image tag/version |
| `PORTAINER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/portainer-ee:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.portainer.entrypoints=websecure`
- `traefik.http.routers.portainer.rule=Host(`portainer-ee.${HOST_DOMAIN}`)`
- `traefik.http.services.portainer.loadbalancer.server.port=9000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PORTAINER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=portainer-ee.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable portainer-ee

# Configure environment variables (if needed)
make scaffold portainer-ee

# Start the service
make up
```
