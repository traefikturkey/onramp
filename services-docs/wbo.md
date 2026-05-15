# Wbo

> Self Hosted whiteboard app

## Links
- [Official Repository](https://github.com/lovasoa/whitebophir)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wbo.yml)

## Docker Images
- `lovasoa/wbo:${WBO_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WBO_CONTAINER_NAME` |  | Container name |
| `WBO_DOCKER_TAG` |  | Docker image tag/version |
| `WBO_RESTART` |  | Container restart policy |
| `WBO_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/wbo/server-data:/opt/app/server-data` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.wbo.entrypoints=websecure`
- `traefik.http.routers.wbo.rule=Host(`${WBO_CONTAINER_NAME:-wbo}.${HOST_DOMAIN}`)`
- `traefik.http.services.wbo.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WBO_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WBO_CONTAINER_NAME:-wbo}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wbo

# Configure environment variables (if needed)
make scaffold wbo

# Start the service
make up
```
