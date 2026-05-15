# Airprint

> Enables apple airprint functionality for non-airprint printers using CUPS and Avahi

## Links
- [Official Repository](https://github.com/RagingTiger/cups-airprint)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/airprint.yml)

## Docker Images
- `ghcr.io/ragingtiger/cups-airprint:${AIRPRINT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AIRPRINT_ADMIN_PASS` |  | Airprint admin pass |
| `AIRPRINT_ADMIN_USER` |  | Service username |
| `AIRPRINT_CONTAINER_NAME` |  | Container name |
| `AIRPRINT_DOCKER_TAG` |  | Docker image tag/version |
| `AIRPRINT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/airprint:/config` - Volume mount
- `./etc/airprint/services:/services` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.airprint.entrypoints=websecure`
- `traefik.http.routers.airprint.rule=Host(`${AIRPRINT_CONTAINER_NAME:-airprint}.${HOST_DOMAIN}`)`
- `traefik.http.services.airprint.loadbalancer.server.port=631`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${AIRPRINT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${AIRPRINT_CONTAINER_NAME:-airprint}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable airprint

# Configure environment variables (if needed)
make scaffold airprint

# Start the service
make up
```
