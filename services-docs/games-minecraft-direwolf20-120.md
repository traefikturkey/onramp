# Games Minecraft Direwolf20 120

> Direwolf20 is a Feed The Beast modpack for Minecraft 1.20.1

## Links
- [Docker Image](https://hub.docker.com/r/itzg/minecraft-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/minecraft-direwolf20-120.yml)

## Docker Images
- `itzg/minecraft-server:${DIREWOLF20_MINECRAFT_VERSION:-java17}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DIREWOLF20_MINECRAFT_CONTAINER_NAME` |  | Container name |
| `DIREWOLF20_MINECRAFT_DIFFICULTY` |  | Direwolf20 minecraft difficulty |
| `DIREWOLF20_MINECRAFT_EXISTING_OPS_FILE` |  | Direwolf20 minecraft existing ops file |
| `DIREWOLF20_MINECRAFT_HOSTNAME` |  | Direwolf20 minecraft hostname |
| `DIREWOLF20_MINECRAFT_NETWORK` |  | Direwolf20 minecraft network |
| `DIREWOLF20_MINECRAFT_OPS_FILE` |  | Direwolf20 minecraft ops file |
| `DIREWOLF20_MINECRAFT_PORT` |  | Service port number |
| `DIREWOLF20_MINECRAFT_RESTART_POLICY` |  | Container restart policy |
| `DIREWOLF20_MINECRAFT_VERSION` |  | Direwolf20 minecraft version |
| `DIREWOLF20_MINECRAFT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `MINECRAFT_HOSTNAME` |  | Minecraft hostname |

## Configuration

### Ports
- `${DIREWOLF20_MINECRAFT_PORT:-25565}:25565`

### Volumes
- `./etc/games/${DIREWOLF20_MINECRAFT_HOSTNAME:-minecraft-direwolf20-120}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DIREWOLF20_MINECRAFT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MINECRAFT_HOSTNAME:-minecraft-direwolf20-120}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-minecraft-direwolf20-120

# Configure environment variables (if needed)
make scaffold games-minecraft-direwolf20-120

# Start the service
make up
```
