# Ongoing

> A self hosted url expander (opposite of url shortener)

## Links
- [Official Repository](https://github.com/traefikturkey/ongoing)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/ongoing.yml)

## Docker Images
- `ghcr.io/traefikturkey/ongoing:${ONGOING_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `ONGOING_CONTAINER_NAME` |  | Container name |
| `ONGOING_DNS_SERVER` |  | Ongoing dns server |
| `ONGOING_DOCKER_TAG` |  | Docker image tag/version |
| `ONGOING_RESTART` |  | Container restart policy |
| `ONGOING_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
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
- `traefik.enable=true`
- `traefik.http.routers.ongoing.entrypoints=websecure`
- `traefik.http.routers.ongoing.rule=Host(`${ONGOING_CONTAINER_NAME:-ongoing}.${HOST_DOMAIN}`)`
- `traefik.http.services.ongoing.loadbalancer.server.port=9380`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ONGOING_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${ONGOING_CONTAINER_NAME:-ongoing}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable ongoing

# Configure environment variables (if needed)
make scaffold ongoing

# Start the service
make up
```
