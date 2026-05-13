# Watchyourlan

> Monitors network devices and services

## Links
- [Official Repository](https://github.com/aceberg/WatchYourLAN)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/watchyourlan.yml)

## Docker Images
- `ghcr.io/aceberg/watchyourlan:${WATCHYOURLAN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WATCHYOURLAN_CONTAINER_NAME` |  | Container name |
| `WATCHYOURLAN_DOCKER_TAG` |  | Docker image tag/version |
| `WATCHYOURLAN_GUIIP` |  | Watchyourlan guiip |
| `WATCHYOURLAN_IFACE` |  | Watchyourlan iface |
| `WATCHYOURLAN_RESTART` |  | Container restart policy |
| `WATCHYOURLAN_SHOUTRRR_URL` |  | Watchyourlan shoutrrr url |
| `WATCHYOURLAN_THEME` |  | Watchyourlan theme |
| `WATCHYOURLAN_TIMEOUT` |  | Watchyourlan timeout |
| `WATCHYOURLAN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/watchyourlan:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.watchyourlan.entrypoints=websecure`
- `traefik.http.routers.watchyourlan.rule=Host(`${WATCHYOURLAN_CONTAINER_NAME:-watchyourlan}.${HOST_DOMAIN}`)`
- `traefik.http.services.watchyourlan.loadbalancer.server.port=8840`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WATCHYOURLAN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WATCHYOURLAN_CONTAINER_NAME:-watchyourlan}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable watchyourlan

# Configure environment variables (if needed)
make scaffold watchyourlan

# Start the service
make up
```
