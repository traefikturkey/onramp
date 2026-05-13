# Infinity

> High-performance embedding inference server supporting multiple models

## Links
- [Official Repository](https://github.com/michaelfeil/infinity)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/infinity.yml)

## Docker Images
- `michaelf34/infinity:${INFINITY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `INFINITY_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `INFINITY_BATCH_SIZE` |  | Infinity batch size |
| `INFINITY_CONTAINER_NAME` |  | Container name |
| `INFINITY_DATA_PATH` |  | Infinity data path |
| `INFINITY_DOCKER_TAG` |  | Docker image tag/version |
| `INFINITY_ENGINE` |  | Infinity engine |
| `INFINITY_GPU_COUNT` |  | Infinity gpu count |
| `INFINITY_MODEL_1` |  | Infinity model 1 |
| `INFINITY_MODEL_2` |  | Infinity model 2 |
| `INFINITY_PORT` |  | Service port number |
| `INFINITY_RESTART` |  | Container restart policy |
| `INFINITY_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `INFINITY_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${INFINITY_PORT:-7997}:7997`

### Volumes
- `${INFINITY_DATA_PATH:-./media/infinity}` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${INFINITY_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.infinity.entrypoints=websecure`
- `traefik.http.routers.infinity.rule=Host(`${INFINITY_CONTAINER_NAME:-infinity}.${HOST_DOMAIN}`)`
- `traefik.http.services.infinity.loadbalancer.server.port=7997`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${INFINITY_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${INFINITY_AUTOHEAL:-true}`
- `joyride.host.name=${INFINITY_CONTAINER_NAME:-infinity}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable infinity

# Configure environment variables (if needed)
make scaffold infinity

# Start the service
make up
```
