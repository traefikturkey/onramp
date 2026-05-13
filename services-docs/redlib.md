# Redlib

> An open source frontend for reddit.

## Links
- [Official Repository](https://github.com/redlib-org/redlib?tab=readme-ov-file#Configuration)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/redlib.yml)

## Docker Images
- `quay.io/redlib/redlib:${REDLIB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `REBLIB_DISABLE_INDEXING` |  | Reblib disable indexing |
| `REDLIB_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `REDLIB_CONTAINER_NAME` |  | Container name |
| `REDLIB_DOCKER_TAG` |  | Docker image tag/version |
| `REDLIB_ENABLE_RSS` |  | Redlib enable rss |
| `REDLIB_FIXED_NAVBAR` |  | Redlib fixed navbar |
| `REDLIB_HOST_NAME` |  | Redlib host name |
| `REDLIB_LAYOUT` |  | Redlib layout |
| `REDLIB_MEM_LIMIT` |  | Redlib mem limit |
| `REDLIB_RESTART` |  | Container restart policy |
| `REDLIB_SFW_ONLY` |  | Redlib sfw only |
| `REDLIB_SUBSCRIPTIONS` |  | Redlib subscriptions |
| `REDLIB_THEME` |  | Redlib theme |
| `REDLIB_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `REDLIB_USE_HLS` |  | Redlib use hls |
| `REDLIB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `REDLIB_WIDE` |  | Redlib wide |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${REDLIB_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.redlib.entrypoints=websecure`
- `traefik.http.routers.redlib.rule=Host(`${REDLIB_HOST_NAME:-redlib}.${HOST_DOMAIN}`)`
- `traefik.http.services.redlib.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${REDLIB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${REDLIB_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${REDLIB_HOST_NAME:-redlib}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable redlib

# Configure environment variables (if needed)
make scaffold redlib

# Start the service
make up
```
