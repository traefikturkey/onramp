# Games Minecraft Bedrock

> Minecraft Bedrock Edition designed for various platforms including mobile and console

## Links
- [Docker Image](https://hub.docker.com/r/itzg/minecraft-bedrock-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/minecraft-bedrock.yml)

## Docker Images
- `itzg/minecraft-bedrock-server:${MINECRAFT_BEDROCK_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MINECRAFT_BEDROCK_CONTAINER_NAME` |  | Container name |
| `MINECRAFT_BEDROCK_DOCKER_TAG` |  | Docker image tag/version |
| `MINECRAFT_BEDROCK_HOSTNAME` |  | Minecraft bedrock hostname |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `19132:19132/udp`

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/games/${MINECRAFT_BEDROCK_HOSTNAME:-minecraft-bedrock}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MINECRAFT_BEDROCK_CONTAINER_NAME:-minecraft-bedrock}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-minecraft-bedrock

# Configure environment variables (if needed)
make scaffold games-minecraft-bedrock

# Start the service
make up
```
