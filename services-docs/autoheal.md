# Autoheal

> Restarts unhealthy docker containers automatically

## Links
- [Official Repository](https://github.com/willfarrell/docker-autoheal)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/autoheal.yml)

## Docker Images
- `willfarrell/autoheal:${AUTOHEAL_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTOHEAL_CONTAINER_LABEL` |  | Enable Autoheal container restart on unhealthy status |
| `AUTOHEAL_CONTAINER_NAME` |  | Container name |
| `AUTOHEAL_DOCKER_TAG` |  | Docker image tag/version |
| `AUTOHEAL_INTERVAL_VALUE` |  | Enable Autoheal container restart on unhealthy status |
| `AUTOHEAL_MEM_LIMIT` |  | Enable Autoheal container restart on unhealthy status |
| `AUTOHEAL_RESTART` |  | Container restart policy |
| `AUTOHEAL_STOP_TIMEOUT` |  | Enable Autoheal container restart on unhealthy status |
| `AUTOHEAL_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=${AUTOHEAL_TRAEFIK_ENABLE:-false}`

## Quick Start

```bash
# Enable the service
make enable autoheal

# Configure environment variables (if needed)
make scaffold autoheal

# Start the service
make up
```
