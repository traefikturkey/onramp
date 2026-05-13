# Ghost

> Headless cms for creating blogs and websites

## Links
- [Docker Image](https://hub.docker.com/_/ghost)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/ghost.yml)

## Docker Images
- `ghost:${GHOST_DOCKER_TAG:-alpine}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GHOST_CONTAINER_NAME` |  | Container name |
| `GHOST_DATABASE_HOST` |  | Ghost database host |
| `GHOST_DATABASE_NAME` |  | Ghost database name |
| `GHOST_DATABASE_PASSWORD` |  | Service password |
| `GHOST_DATABASE_USER` |  | Service username |
| `GHOST_DOCKER_TAG` |  | Docker image tag/version |
| `GHOST_RESTART` |  | Container restart policy |
| `GHOST_URL` |  | Ghost url |
| `GHOST_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/ghost:/var/lib/ghost/content` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.ghost.entrypoints=websecure`
- `traefik.http.routers.ghost.rule=Host(`${GHOST_CONTAINER_NAME:-ghost}.${HOST_DOMAIN}`)`
- `traefik.http.services.ghost.loadbalancer.server.port=2368`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GHOST_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GHOST_CONTAINER_NAME:-ghost}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable ghost

# Configure environment variables (if needed)
make scaffold ghost

# Start the service
make up
```
