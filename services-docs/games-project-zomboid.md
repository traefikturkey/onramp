# Games Project Zomboid

> Project Zomboid is an open-world isometric zombie survival game

## Links
- [Official Repository](https://github.com/Renegade-Master/zomboid-dedicated-server)
- [Docker Image](https://hub.docker.com/r/renegademaster/zomboid-dedicated-server)
- [Official Documentation](https://pzwiki.net/wiki/Dedicated_server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/project-zomboid.yml)

## Docker Images
- `renegademaster/zomboid-dedicated-server:${PROJECT_ZOMBOID_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PROJECT_ZOMBOID_ADMIN_PASSWORD` |  | Service password |
| `PROJECT_ZOMBOID_ADMIN_USERNAME` |  | Service username |
| `PROJECT_ZOMBOID_AUTOSAVE_INTERVAL` |  | Project zomboid autosave interval |
| `PROJECT_ZOMBOID_CONTAINER_NAME` |  | Container name |
| `PROJECT_ZOMBOID_DEFAULT_PORT` |  | Service port number |
| `PROJECT_ZOMBOID_DOCKER_TAG` |  | Docker image tag/version |
| `PROJECT_ZOMBOID_HOSTNAME` |  | Project zomboid hostname |
| `PROJECT_ZOMBOID_MAX_PLAYERS` |  | Project zomboid max players |
| `PROJECT_ZOMBOID_MAX_RAM` |  | Project zomboid max ram |
| `PROJECT_ZOMBOID_MOD_NAMES` |  | Project zomboid mod names |
| `PROJECT_ZOMBOID_MOD_WORKSHOP_IDS` |  | Project zomboid mod workshop ids |
| `PROJECT_ZOMBOID_PAUSE_ON_EMPTY` |  | Project zomboid pause on empty |
| `PROJECT_ZOMBOID_PUBLIC_SERVER` |  | Project zomboid public server |
| `PROJECT_ZOMBOID_RCON_PASSWORD` |  | Service password |
| `PROJECT_ZOMBOID_RCON_PORT` |  | Service port number |
| `PROJECT_ZOMBOID_RESTART_POLICY` |  | Container restart policy |
| `PROJECT_ZOMBOID_SERVER_NAME` |  | Project zomboid server name |
| `PROJECT_ZOMBOID_SERVER_PASSWORD` |  | Service password |
| `PROJECT_ZOMBOID_STEAM_VAC` |  | Project zomboid steam vac |
| `PROJECT_ZOMBOID_UDP_PORT` |  | Service port number |
| `PROJECT_ZOMBOID_USE_STEAM` |  | Project zomboid use steam |
| `PROJECT_ZOMBOID_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${PROJECT_ZOMBOID_DEFAULT_PORT:-16261}:16261/udp`
- `${PROJECT_ZOMBOID_UDP_PORT:-16262}:16262/udp`

### Volumes
- `./etc/games/${PROJECT_ZOMBOID_HOSTNAME:-project-zomboid}/ZomboidDedicatedServer` - Volume mount
- `./etc/games/${PROJECT_ZOMBOID_HOSTNAME:-project-zomboid}/Zomboid` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PROJECT_ZOMBOID_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PROJECT_ZOMBOID_HOSTNAME:-project-zomboid}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-project-zomboid

# Configure environment variables (if needed)
make scaffold games-project-zomboid

# Start the service
make up
```
