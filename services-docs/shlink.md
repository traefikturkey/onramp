# Shlink

> Self-Hosted URL shortener.

## Links
- [Official Documentation](https://shlink.io/documentation/install-docker-image/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/shlink.yml)

## Docker Images
- `ghcr.io/shlinkio/shlink:${SHLINK_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SHLINK_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `SHLINK_CONTAINER_NAME` |  | Container name |
| `SHLINK_DEFAULT_DOMAIN` |  | Shlink default domain |
| `SHLINK_DOCKER_TAG` |  | Docker image tag/version |
| `SHLINK_GEOLITE_KEY` |  | Shlink geolite key |
| `SHLINK_HOST_NAME` |  | Shlink host name |
| `SHLINK_HTTPS_ENABLED` |  | Shlink https enabled |
| `SHLINK_MEM_LIMIT` |  | Shlink mem limit |
| `SHLINK_RESTART` |  | Container restart policy |
| `SHLINK_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `SHLINK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/shlink:/etc/shlink/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SHLINK_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.shlink.entrypoints=websecure`
- `traefik.http.routers.shlink.rule=Host(`${SHLINK_HOST_NAME:-shlink}.${HOST_DOMAIN}`)`
- `traefik.http.services.shlink.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SHLINK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${SHLINK_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${SHLINK_HOST_NAME:-shlink}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable shlink

# Configure environment variables (if needed)
make scaffold shlink

# Start the service
make up
```
