# Yacht

> Web interface for managing docker containers

## Links
- [Official Repository](https://github.com/SelfhostedPro/Yacht)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/yacht.yml)

## Docker Images
- `ghcr.io/selfhostedpro/yacht:${YACHT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `YACHT_CONTAINER_NAME` |  | Container name |
| `YACHT_DOCKER_TAG` |  | Docker image tag/version |

## Configuration

### Volumes
- `./etc/yacht:/config` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.yacht.entrypoints=websecure`
- `traefik.http.routers.yacht.rule=Host(`${YACHT_CONTAINER_NAME:-yacht}.${HOST_DOMAIN}`)`
- `traefik.http.routers.yacht.service=yacht`
- `traefik.http.routers.yacht.tls=true`
- `traefik.http.services.yacht.loadbalancer.server.port=8000`

**Other Labels:**
- `joyride.host.name=${YACHT_CONTAINER_NAME:-yacht}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable yacht

# Configure environment variables (if needed)
make scaffold yacht

# Start the service
make up
```
