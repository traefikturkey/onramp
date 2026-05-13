# Ittools

> Useful tools for developer and people working in IT.

## Links
- [Official Repository](https://github.com/CorentinTh/it-tools)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/ittools.yml)

## Docker Images
- `ghcr.io/corentinth/it-tools:${ITTOOLS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `ITTOOLS_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `ITTOOLS_CONTAINER_NAME` |  | Container name |
| `ITTOOLS_DOCKER_TAG` |  | Docker image tag/version |
| `ITTOOLS_HOST_NAME` |  | Ittools host name |
| `ITTOOLS_MEM_LIMIT` |  | Ittools mem limit |
| `ITTOOLS_RESTART` |  | Container restart policy |
| `ITTOOLS_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `ITTOOLS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
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
- `traefik.enable=${ITTOOLS_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.ittools.entrypoints=websecure`
- `traefik.http.routers.ittools.rule=Host(`${ITTOOLS_HOST_NAME:-ittools}.${HOST_DOMAIN}`)`
- `traefik.http.services.ittools.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ITTOOLS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${ITTOOLS_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${ITTOOLS_HOST_NAME:-ittools}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable ittools

# Configure environment variables (if needed)
make scaffold ittools

# Start the service
make up
```
