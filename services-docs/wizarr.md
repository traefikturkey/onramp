# Wizarr

> Wizarr is an advanced user invitation and management system for Jellyfin, Plex, Emby etc.

## Links
- [Official Repository](https://github.com/wizarrrr/wizarr)
- [Official Documentation](https://docs.wizarr.dev/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wizarr.yml)

## Docker Images
- `ghcr.io/wizarrrr/wizarr:${WIZARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WIZARR_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `WIZARR_CONTAINER_NAME` |  | Container name |
| `WIZARR_DOCKER_TAG` |  | Docker image tag/version |
| `WIZARR_HOST_NAME` |  | Wizarr host name |
| `WIZARR_MEM_LIMIT` |  | Wizarr mem limit |
| `WIZARR_RESTART` |  | Container restart policy |
| `WIZARR_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `WIZARR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/wizarr:/data/database` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${WIZARR_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.wizarr.entrypoints=websecure`
- `traefik.http.routers.wizarr.rule=Host(`${WIZARR_HOST_NAME:-wizarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.wizarr.loadbalancer.server.port=5690`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WIZARR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${WIZARR_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${WIZARR_HOST_NAME:-wizarr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wizarr

# Configure environment variables (if needed)
make scaffold wizarr

# Start the service
make up
```
