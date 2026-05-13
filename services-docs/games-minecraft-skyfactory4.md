# Games Minecraft Skyfactory4

> SkyFactory 4 is a Feed The Beast modpack for Minecraft 1.12.2

## Links
- [Docker Image](https://hub.docker.com/r/itzg/minecraft-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/minecraft-skyfactory4.yml)

## Docker Images
- `itzg/minecraft-server:${SKYFACTORY_MINECRAFT_VERSION:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MINECRAFT_FLOODGATE_PORT` |  | Service port number |
| `MINECRAFT_HOSTNAME` |  | Minecraft hostname |
| `SKYFACTORY_MINECRAFT_CONSOLE` |  | Skyfactory minecraft console |
| `SKYFACTORY_MINECRAFT_CONTAINER_NAME` |  | Container name |
| `SKYFACTORY_MINECRAFT_ENABLE_RCON` |  | Skyfactory minecraft enable rcon |
| `SKYFACTORY_MINECRAFT_HOSTNAME` |  | Skyfactory minecraft hostname |
| `SKYFACTORY_MINECRAFT_MEMORY` |  | Skyfactory minecraft memory |
| `SKYFACTORY_MINECRAFT_NETWORK` |  | Skyfactory minecraft network |
| `SKYFACTORY_MINECRAFT_PORT` |  | Service port number |
| `SKYFACTORY_MINECRAFT_RESTART_POLICY` |  | Container restart policy |
| `SKYFACTORY_MINECRAFT_TYPE` |  | Skyfactory minecraft type |
| `SKYFACTORY_MINECRAFT_VERSION` |  | Skyfactory minecraft version |
| `SKYFACTORY_MINECRAFT_VIEW_DISTANCE` |  | Skyfactory minecraft view distance |
| `SKYFACTORY_MINECRAFT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `${SKYFACTORY_MINECRAFT_PORT:-25565}:25565`

### Volumes
- `./etc/games/${SKYFACTORY_MINECRAFT_HOSTNAME:-minecraft_skyfactory4}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SKYFACTORY_MINECRAFT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MINECRAFT_HOSTNAME:-minecraft_skyfactory4}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-minecraft-skyfactory4

# Configure environment variables (if needed)
make scaffold games-minecraft-skyfactory4

# Start the service
make up
```
