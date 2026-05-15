# Doku

> Disk usage dashboard

## Links
- [Official Repository](https://github.com/amerkurev/doku)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/doku.yml)

## Docker Images
- `amerkurev/doku:${DOKU_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOKU_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DOKU_CONTAINER_NAME` |  | Container name |
| `DOKU_DOCKER_TAG` |  | Docker image tag/version |
| `DOKU_MEM_LIMIT` |  | Doku mem limit |
| `DOKU_RESTART` |  | Container restart policy |
| `DOKU_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `DOKU_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `/:/hostroot` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DOKU_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.doku.entrypoints=websecure`
- `traefik.http.routers.doku.rule=Host(`${DOKU_CONTAINER_NAME:-doku}.${HOST_DOMAIN}`)`
- `traefik.http.services.doku.loadbalancer.server.port=9090`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOKU_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DOKU_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${DOKU_CONTAINER_NAME:-doku}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable doku

# Configure environment variables (if needed)
make scaffold doku

# Start the service
make up
```
