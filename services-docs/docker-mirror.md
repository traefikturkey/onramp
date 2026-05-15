# Docker Mirror

> docker mirror / registry for caching docker images

## Links
- [Docker Image](https://hub.docker.com/_/registry)
- [Official Documentation](https://docs.docker.com/docker-hub/image-library/mirror/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/docker-mirror.yml)

## Docker Images
- `registry:${DOCKER_MIRROR_DOCKER_TAG:-2}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKER_MIRROR_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DOCKER_MIRROR_CONTAINER_NAME` |  | Container name |
| `DOCKER_MIRROR_DATA_PATH` |  | Docker mirror data path |
| `DOCKER_MIRROR_DOCKER_TAG` |  | Docker image tag/version |
| `DOCKER_MIRROR_HOST_NAME` |  | Docker mirror host name |
| `DOCKER_MIRROR_MEM_LIMIT` |  | Docker mirror mem limit |
| `DOCKER_MIRROR_RESTART` |  | Container restart policy |
| `DOCKER_MIRROR_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `DOCKER_MIRROR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/docker-mirror/registry:/etc/docker/registry` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `${DOCKER_MIRROR_DATA_PATH:-./etc/docker-mirror/registry_data}` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DOCKER_MIRROR_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.docker-mirror.entrypoints=websecure`
- `traefik.http.routers.docker-mirror.rule=Host(`${DOCKER_MIRROR_HOST_NAME:-docker-mirror}.${HOST_DOMAIN}`)`
- `traefik.http.services.docker-mirror.loadbalancer.server.port=5000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCKER_MIRROR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DOCKER_MIRROR_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${DOCKER_MIRROR_HOST_NAME:-docker-mirror}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable docker-mirror

# Configure environment variables (if needed)
make scaffold docker-mirror

# Start the service
make up
```
