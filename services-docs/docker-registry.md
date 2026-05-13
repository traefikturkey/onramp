# Docker Registry

> Registry for storing and distributing container images

## Links
- [Docker Image](https://hub.docker.com/_/registry)
- [Official Documentation](https://docs.docker.com/registry/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/docker-registry.yml)

## Docker Images
- `registry:${DOCKER_REGISTRY_DOCKER_TAG:-2}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKER_REGISTRY_AUTH_PASS` |  | Docker registry auth pass |
| `DOCKER_REGISTRY_AUTH_USER` |  | Service username |
| `DOCKER_REGISTRY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DOCKER_REGISTRY_CONTAINER_NAME` |  | Container name |
| `DOCKER_REGISTRY_DOCKER_TAG` |  | Docker image tag/version |
| `DOCKER_REGISTRY_PATH` |  | Docker registry path |
| `DOCKER_REGISTRY_RESTART` |  | Container restart policy |
| `DOCKER_REGISTRY_STORAGE_DELETE_ENABLED` |  | Docker registry storage delete enabled |
| `DOCKER_REGISTRY_STORAGE_FILESYSTEM_ROOTDIRECTORY` |  | Docker registry storage filesystem rootdirectory |
| `DOCKER_REGISTRY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `DOCKER_REGISTRY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${DOCKER_REGISTRY_PATH:-./etc/docker-registry}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DOCKER_REGISTRY_TRAEFIK_ENABLED:-true}`
- `traefik.http.middlewares.auth.basicauth.users=${DOCKER_REGISTRY_AUTH_USER:-admin}:${DOCKER_REGISTRY_AUTH_PASS:-password}}`
- `traefik.http.routers.registry.entrypoints=websecure`
- `traefik.http.routers.registry.rule=Host(`${DOCKER_REGISTRY_CONTAINER_NAME:-registry}.${HOST_DOMAIN}`)`
- `traefik.http.services.registry.loadbalancer.server.port=5000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCKER_REGISTRY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DOCKER_REGISTRY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${DOCKER_REGISTRY_CONTAINER_NAME:-registry}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable docker-registry

# Configure environment variables (if needed)
make scaffold docker-registry

# Start the service
make up
```
