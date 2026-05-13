# Games Minecraft

> Minecraft is a game about placing blocks and going on adventures

## Links
- [Docker Image](https://hub.docker.com/r/itzg/minecraft-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/minecraft.yml)

## Docker Images
- `itzg/minecraft-server:${MINCRAFT_VERSION:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FACTORIO_NETWORK` |  | Factorio network |
| `HOST_DOMAIN` |  | Host domain for service access |
| `MINCRAFT_CONSOLE` |  | Mincraft console |
| `MINCRAFT_CONTAINER_NAME` |  | Container name |
| `MINCRAFT_ENABLE_RCON` |  | Mincraft enable rcon |
| `MINCRAFT_GEYSER_PORT` |  | Service port number |
| `MINCRAFT_MEMORY` |  | Mincraft memory |
| `MINCRAFT_PORT` |  | Service port number |
| `MINCRAFT_RESTART_POLICY` |  | Container restart policy |
| `MINCRAFT_TYPE` |  | Mincraft type |
| `MINCRAFT_VANILLATWEAKS_SHARECODE` |  | Mincraft vanillatweaks sharecode |
| `MINCRAFT_VERSION` |  | Mincraft version |
| `MINCRAFT_VIEW_DISTANCE` |  | Mincraft view distance |
| `MINECRAFT_HOSTNAME` |  | Minecraft hostname |
| `MINECRAFT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `${MINCRAFT_PORT:-25565}:25565`

### Volumes
- `./etc/games/${MINECRAFT_HOSTNAME:-minecraft}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MINECRAFT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MINECRAFT_HOSTNAME:-minecraft}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-minecraft

# Configure environment variables (if needed)
make scaffold games-minecraft

# Start the service
make up
```
