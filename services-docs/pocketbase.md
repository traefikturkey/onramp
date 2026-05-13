# Pocketbase

> Open Source realtime backend in 1 file

## Links
- [Official Repository](https://github.com/pocketbase/pocketbase)
- [Official Documentation](https://pocketbase.io/docs/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pocketbase.yml)

## Docker Images
- `ghcr.io/muchobien/pocketbase:${POCKETBASE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `POCKETBASE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `POCKETBASE_CONTAINER_NAME` |  | Container name |
| `POCKETBASE_DOCKER_TAG` |  | Docker image tag/version |
| `POCKETBASE_ENCRYPTION_KEY` |  | Pocketbase encryption key |
| `POCKETBASE_HOST_NAME` |  | Pocketbase host name |
| `POCKETBASE_MEM_LIMIT` |  | Pocketbase mem limit |
| `POCKETBASE_RESTART` |  | Container restart policy |
| `POCKETBASE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `POCKETBASE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/pocketbase/data:/pb_data` - Data storage
- `./etc/pocketbase/public:/pb_public` - Volume mount
- `./etc/pocketbase/hooks:/pb_hooks` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${POCKETBASE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.pocketbase.entrypoints=websecure`
- `traefik.http.routers.pocketbase.rule=Host(`${POCKETBASE_HOST_NAME:-pocketbase}.${HOST_DOMAIN}`)`
- `traefik.http.services.pocketbase.loadbalancer.server.port=8090`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${POCKETBASE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${POCKETBASE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${POCKETBASE_HOST_NAME:-pocketbase}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pocketbase

# Configure environment variables (if needed)
make scaffold pocketbase

# Start the service
make up
```
