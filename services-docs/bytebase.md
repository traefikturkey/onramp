# Bytebase

> Database CI/CD and Security at Scale

## Links
- [Official Documentation](https://www.bytebase.com)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/bytebase.yml)

## Docker Images
- `bytebase/bytebase:${BYTEBASE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BB_EXTERNAL_URL` |  | Bb external url |
| `BB_PG` |  | Bb pg |
| `BYTEBASE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `BYTEBASE_CONTAINER_NAME` |  | Container name |
| `BYTEBASE_DOCKER_TAG` |  | Docker image tag/version |
| `BYTEBASE_HOST_NAME` |  | Bytebase host name |
| `BYTEBASE_RESTART` |  | Container restart policy |
| `BYTEBASE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `BYTEBASE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/bytebase/data:/var/opt/bytebase` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${BYTEBASE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.bytebase.entrypoints=websecure`
- `traefik.http.routers.bytebase.rule=Host(`${BYTEBASE_HOST_NAME:-bytebase}.${HOST_DOMAIN}`)`
- `traefik.http.services.bytebase.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BYTEBASE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${BYTEBASE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${BYTEBASE_HOST_NAME:-bytebase}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable bytebase

# Configure environment variables (if needed)
make scaffold bytebase

# Start the service
make up
```
