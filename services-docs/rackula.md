# Rackula

> Drag and drop rack visualizer for homelabs

## Links
- [Official Repository](https://github.com/RackulaLives/Rackula)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/rackula.yml)

## Docker Images
- `ghcr.io/rackulalives/rackula:${RACKULA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `RACKULA_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `RACKULA_CONTAINER_NAME` | rackula | Container name |
| `RACKULA_DOCKER_TAG` | latest | Docker image tag/version |
| `RACKULA_HOST_NAME` | rackula | Rackula host name |
| `RACKULA_MEM_LIMIT` | 128m | Rackula mem limit |
| `RACKULA_RESTART` | unless-stopped | Container restart policy |
| `RACKULA_TRAEFIK_ENABLED` | true | Enable Traefik reverse proxy |
| `RACKULA_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${RACKULA_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.rackula.entrypoints=websecure`
- `traefik.http.routers.rackula.rule=Host(`${RACKULA_HOST_NAME:-rackula}.${HOST_DOMAIN}`)`
- `traefik.http.services.rackula.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${RACKULA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${RACKULA_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${RACKULA_HOST_NAME:-rackula}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable rackula

# Configure environment variables (if needed)
make scaffold rackula

# Start the service
make up
```
