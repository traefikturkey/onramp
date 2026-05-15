# Convertx

> A self-hosted online file converter.

## Links
- [Official Repository](https://github.com/C4illin/ConvertX)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/convertx.yml)

## Docker Images
- `ghcr.io/c4illin/convertx:${CONVERTX_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CONVERTX_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `CONVERTX_CONTAINER_NAME` |  | Container name |
| `CONVERTX_DOCKER_TAG` |  | Docker image tag/version |
| `CONVERTX_HOST_NAME` |  | Convertx host name |
| `CONVERTX_JWT_SECRET` |  | Convertx jwt secret |
| `CONVERTX_MEM_LIMIT` |  | Convertx mem limit |
| `CONVERTX_RESTART` |  | Container restart policy |
| `CONVERTX_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `CONVERTX_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/convertx:/app/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CONVERTX_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.convertx.entrypoints=websecure`
- `traefik.http.routers.convertx.rule=Host(`${CONVERTX_HOST_NAME:-convertx}.${HOST_DOMAIN}`)`
- `traefik.http.services.convertx.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CONVERTX_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${CONVERTX_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${CONVERTX_HOST_NAME:-convertx}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable convertx

# Configure environment variables (if needed)
make scaffold convertx

# Start the service
make up
```
