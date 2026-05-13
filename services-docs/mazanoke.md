# Mazanoke

> A self-hosted local image optimizer that runs in your browser.

## Links
- [Official Repository](https://github.com/civilblur/mazanoke)
- [Official Documentation](https://mazanoke.com/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mazanoke.yml)

## Docker Images
- `ghcr.io/civilblur/mazanoke:${MAZANOKE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MAZANOKE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `MAZANOKE_CONTAINER_NAME` |  | Container name |
| `MAZANOKE_DOCKER_TAG` |  | Docker image tag/version |
| `MAZANOKE_HOST_NAME` |  | Mazanoke host name |
| `MAZANOKE_MEM_LIMIT` |  | Mazanoke mem limit |
| `MAZANOKE_RESTART` |  | Container restart policy |
| `MAZANOKE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `MAZANOKE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${MAZANOKE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.mazanoke.entrypoints=websecure`
- `traefik.http.routers.mazanoke.rule=Host(`${MAZANOKE_HOST_NAME:-mazanoke}.${HOST_DOMAIN}`)`
- `traefik.http.services.mazanoke.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MAZANOKE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${MAZANOKE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${MAZANOKE_HOST_NAME:-mazanoke}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable mazanoke

# Configure environment variables (if needed)
make scaffold mazanoke

# Start the service
make up
```
