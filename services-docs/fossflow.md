# Fossflow

> Open-source Progressive Web App (PWA) for creating isometric diagrams.

## Links
- [Official Repository](https://github.com/TheFitzZZ/FossFLOWDocker)
- [Docker Image](https://hub.docker.com/r/fitzzz/fossflow)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/fossflow.yml)

## Docker Images
- `fitzzz/fossflow:${FOSSFLOW_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FOSSFLOW_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `FOSSFLOW_CONTAINER_NAME` |  | Container name |
| `FOSSFLOW_DOCKER_TAG` |  | Docker image tag/version |
| `FOSSFLOW_HOST_NAME` |  | Fossflow host name |
| `FOSSFLOW_MEM_LIMIT` |  | Fossflow mem limit |
| `FOSSFLOW_RESTART` |  | Container restart policy |
| `FOSSFLOW_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `FOSSFLOW_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${FOSSFLOW_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.fossflow.entrypoints=websecure`
- `traefik.http.routers.fossflow.rule=Host(`${FOSSFLOW_HOST_NAME:-fossflow}.${HOST_DOMAIN}`)`
- `traefik.http.services.fossflow.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FOSSFLOW_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${FOSSFLOW_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${FOSSFLOW_HOST_NAME:-fossflow}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable fossflow

# Configure environment variables (if needed)
make scaffold fossflow

# Start the service
make up
```
