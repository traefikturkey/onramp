# Gatus

> Monitors services and sends alerts

## Links
- [Official Repository](https://github.com/TwiN/gatus)
- [Official Documentation](https://technotim.live/posts/gatus-uptime-monitoring/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/gatus.yml)

## Docker Images
- `ghcr.io/twin/gatus:${GATUS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GATUS_CONTAINER_NAME` |  | Container name |
| `GATUS_DOCKER_TAG` |  | Docker image tag/version |
| `GATUS_POSTGRES_DB` |  | PostgreSQL database name |
| `GATUS_POSTGRES_PASSWORD` |  | Service password |
| `GATUS_POSTGRES_USER` |  | Service username |
| `GATUS_RESTART` |  | Container restart policy |
| `GATUS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `../etc/gatus:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.gatus.entrypoints=websecure`
- `traefik.http.routers.gatus.rule=Host(`${GATUS_CONTAINER_NAME:-gatus}.${HOST_DOMAIN}`)`
- `traefik.http.services.gatus.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GATUS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GATUS_CONTAINER_NAME:-gatus}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable gatus

# Configure environment variables (if needed)
make scaffold gatus

# Start the service
make up
```
