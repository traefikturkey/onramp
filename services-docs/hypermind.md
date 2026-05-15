# Hypermind

> P2P swarm counter - shows how many Docker users are connected globally

## Links
- [Official Repository](https://github.com/lklynet/hypermind)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/hypermind.yml)

## Docker Images
- `ghcr.io/lklynet/hypermind:${HYPERMIND_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `HYPERMIND_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `HYPERMIND_CONTAINER_NAME` |  | Container name |
| `HYPERMIND_DOCKER_TAG` |  | Docker image tag/version |
| `HYPERMIND_MAX_PEERS` |  | Hypermind max peers |
| `HYPERMIND_PORT` | 3000 | Service port number |
| `HYPERMIND_RESTART` |  | Container restart policy |
| `HYPERMIND_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `HYPERMIND_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Labels
**Traefik Configuration:**
- `traefik.enable=${HYPERMIND_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.hypermind.entrypoints=websecure`
- `traefik.http.routers.hypermind.rule=Host(`${HYPERMIND_CONTAINER_NAME:-hypermind}.${HOST_DOMAIN}`)`
- `traefik.http.services.hypermind.loadbalancer.server.port=${HYPERMIND_PORT:-3000}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HYPERMIND_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${HYPERMIND_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${HYPERMIND_CONTAINER_NAME:-hypermind}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable hypermind

# Configure environment variables (if needed)
make scaffold hypermind

# Start the service
make up
```
