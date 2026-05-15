# Dozzle

> Web-based docker container log viewer

## Links
- [Official Repository](https://github.com/amir20/dozzle)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dozzle.yml)

## Docker Images
- `ghcr.io/amir20/dozzle:${DOZZLE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOZZLE_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `DOZZLE_CONTAINER_NAME` |  | Container name |
| `DOZZLE_DOCKER_TAG` |  | Docker image tag/version |
| `DOZZLE_LEVEL` |  | Dozzle level |
| `DOZZLE_MEM_LIMIT` |  | Dozzle mem limit |
| `DOZZLE_REMOTE_AGENT` | ${DOZZLE_REMOTE_AGENT:-} | Dozzle remote agent |
| `DOZZLE_RESTART` |  | Container restart policy |
| `DOZZLE_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `DOZZLE_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DOZZLE_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.dozzle.entrypoints=websecure`
- `traefik.http.routers.dozzle.rule=Host(`${DOZZLE_CONTAINER_NAME:-dozzle}.${HOST_DOMAIN}`)`
- `traefik.http.services.dozzle.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOZZLE_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${DOZZLE_AUTOHEAL:-true}`
- `joyride.host.name=${DOZZLE_CONTAINER_NAME:-dozzle}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable dozzle

# Configure environment variables (if needed)
make scaffold dozzle

# Start the service
make up
```
