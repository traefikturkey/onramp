# Rwmarkable

> A simple, self-hosted app for your checklists and notes

## Links
- [Official Repository](https://github.com/fccview/rwMarkable)
- [Official Documentation](https://rwmarkable.vercel.app/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/rwmarkable.yml)

## Docker Images
- `ghcr.io/fccview/rwmarkable:${RWMARKABLE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `RWMARKABLE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `RWMARKABLE_CONTAINER_NAME` |  | Container name |
| `RWMARKABLE_DOCKER_TAG` |  | Docker image tag/version |
| `RWMARKABLE_HOST_NAME` |  | Rwmarkable host name |
| `RWMARKABLE_MEM_LIMIT` |  | Rwmarkable mem limit |
| `RWMARKABLE_RESTART` |  | Container restart policy |
| `RWMARKABLE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `RWMARKABLE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/rwmarkable/data:/app/data` - Data storage
- `./etc/rwmarkable/config:/app/config` - Configuration files
- `./etc/rwmarkable/cache:/app/.next/cache` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${RWMARKABLE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.rwmarkable.entrypoints=websecure`
- `traefik.http.routers.rwmarkable.rule=Host(`${RWMARKABLE_HOST_NAME:-rwmarkable}.${HOST_DOMAIN}`)`
- `traefik.http.services.rwmarkable.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${RWMARKABLE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${RWMARKABLE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${RWMARKABLE_HOST_NAME:-rwmarkable}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable rwmarkable

# Configure environment variables (if needed)
make scaffold rwmarkable

# Start the service
make up
```
