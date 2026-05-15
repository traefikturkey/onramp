# Heimdall

> Dashboard for organizing web applications

## Links
- [Official Repository](https://github.com/linuxserver/Heimdall)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/heimdall.yml)

## Docker Images
- `lscr.io/linuxserver/heimdall:${HEIMDALL_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEIMDALL_CONTAINER_NAME` |  | Container name |
| `HEIMDALL_DOCKER_TAG` |  | Docker image tag/version |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Volumes
- `./etc/heimdall:/config` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.heimdall.entrypoints=websecure`
- `traefik.http.routers.heimdall.rule=Host(`${HEIMDALL_CONTAINER_NAME:-heimdall}.${HOST_DOMAIN}`)`
- `traefik.http.routers.heimdall.service=heimdall`
- `traefik.http.routers.heimdall.tls=true`
- `traefik.http.services.heimdall.loadbalancer.server.port=80`

**Other Labels:**
- `joyride.host.name=${HEIMDALL_CONTAINER_NAME:-heimdall}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable heimdall

# Configure environment variables (if needed)
make scaffold heimdall

# Start the service
make up
```
