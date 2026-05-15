# Games Factorio

> Factorio is a game about building and managing factories on an alien planet

## Links
- [Docker Image](https://hub.docker.com/r/goofball222/factorio)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/factorio.yml)

## Docker Images
- `goofball222/factorio:${FACTORIO_VERSION:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FACTORIO_CONTAINER_NAME` |  | Container name |
| `FACTORIO_HOSTNAME` |  | Factorio hostname |
| `FACTORIO_PORT_27015` |  | Service port number |
| `FACTORIO_PORT_34197` |  | Service port number |
| `FACTORIO_RESTART_POLICY` |  | Container restart policy |
| `FACTORIO_VERSION` |  | Factorio version |
| `FACTORIO_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${FACTORIO_PORT_27015:-27015}:27015`
- `${FACTORIO_PORT_34197:-34197}:34197/udp`

### Volumes
- `./etc/games/${FACTORIO_HOSTNAME:-factorio}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FACTORIO_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FACTORIO_HOSTNAME:-factorio}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-factorio

# Configure environment variables (if needed)
make scaffold games-factorio

# Start the service
make up
```
