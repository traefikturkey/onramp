# Actual

> Money Management software

## Links
- [Official Repository](https://github.com/actualbudget/actual)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/actual.yml)

## Docker Images
- `ghcr.io/actualbudget/actual-server:latest`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ACTUAL_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `ACTUAL_CONTAINER_NAME` |  | Container name |
| `ACTUAL_RESTART` |  | Container restart policy |
| `ACTUAL_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `ACTUAL_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/actual/data:/data` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${ACTUAL_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.actual.entrypoints=websecure`
- `traefik.http.routers.actual.rule=Host(`${ACTUAL_CONTAINER_NAME:-actual}.${HOST_DOMAIN}`)`
- `traefik.http.services.actual.loadbalancer.server.port=5006`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ACTUAL_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${ACTUAL_AUTOHEAL:-true}`
- `joyride.host.name=${ACTUAL_CONTAINER_NAME:-actual}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable actual

# Configure environment variables (if needed)
make scaffold actual

# Start the service
make up
```
