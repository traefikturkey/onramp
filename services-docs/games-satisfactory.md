# Games Satisfactory

> Satisfactory is a first-person open-world factory building game with a dash of exploration and combat

## Links
- [Official Repository](https://github.com/wolveix/satisfactory-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/satisfactory.yml)

## Docker Images
- `wolveix/satisfactory-server:${SATISFACTORY_VERSION:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SATISFACTORY_AUTOPAUSE` |  | Satisfactory autopause |
| `SATISFACTORY_AUTOSAVEINTERVAL` |  | Satisfactory autosaveinterval |
| `SATISFACTORY_AUTOSAVENUM` |  | Satisfactory autosavenum |
| `SATISFACTORY_AUTOSAVEONDISCONNECT` |  | Satisfactory autosaveondisconnect |
| `SATISFACTORY_CONTAINER_NAME` |  | Container name |
| `SATISFACTORY_DISABLESEASONALEVENTS` |  | Satisfactory disableseasonalevents |
| `SATISFACTORY_HOSTNAME` |  | Satisfactory hostname |
| `SATISFACTORY_MAXPLAYERS` |  | Satisfactory maxplayers |
| `SATISFACTORY_PORT_15000` |  | Service port number |
| `SATISFACTORY_PORT_15777` |  | Service port number |
| `SATISFACTORY_PORT_7777` |  | Service port number |
| `SATISFACTORY_RESTART_POLICY` |  | Container restart policy |
| `SATISFACTORY_SKIPUPDATE` |  | Satisfactory skipupdate |
| `SATISFACTORY_STEAMBETA` |  | Satisfactory steambeta |
| `SATISFACTORY_VERSION` |  | Satisfactory version |
| `SATISFACTORY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `${SATISFACTORY_PORT_7777:-7777}:7777/udp`
- `${SATISFACTORY_PORT_15000:-15000}:15000/udp`
- `${SATISFACTORY_PORT_15777:-15777}:15777/udp`

### Volumes
- `./etc/games/${SATISFACTORY_HOSTNAME:-satisfactory}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SATISFACTORY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SATISFACTORY_HOSTNAME:-satisfactory}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-satisfactory

# Configure environment variables (if needed)
make scaffold games-satisfactory

# Start the service
make up
```
