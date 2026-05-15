# Games Valheim

> Valheim is a game about exploring a huge fantasy world inspired by norse mythology and viking culture

## Links
- [Official Repository](https://github.com/lloesche/valheim-server-docker/blob/main/valheim.env.example)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/valheim.yml)

## Docker Images
- `ghcr.io/lloesche/valheim-server:${VALHEIM_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `VALHEIM_CONTAINER_NAME` |  | Container name |
| `VALHEIM_DOCKER_TAG` |  | Docker image tag/version |
| `VALHEIM_RESTART` |  | Container restart policy |
| `VALHEIM_SERVER_NAME` |  | Valheim server name |
| `VALHEIM_SERVER_PASS` |  | Valheim server pass |
| `VALHEIM_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `VALHEIM_WORLD_NAME` |  | Valheim world name |

## Configuration

### Ports
- `2456-2457:2456-2457/udp`

### Volumes
- `./etc/games/valheim/config:/config` - Configuration files
- `./etc/games/valheim/data:/opt/valheim` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.valheim.entrypoints=websecure`
- `traefik.http.routers.valheim.rule=Host(`${VALHEIM_CONTAINER_NAME:-valheim}.${HOST_DOMAIN}`)`
- `traefik.http.services.valheim.loadbalancer.server.port=9001`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${VALHEIM_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${VALHEIM_CONTAINER_NAME:-valheim}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-valheim

# Configure environment variables (if needed)
make scaffold games-valheim

# Start the service
make up
```
