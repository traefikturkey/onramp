# Games Mindustry

> Mindustry is a sandbox tower defense game

## Links
- [Official Repository](https://github.com/ich777/docker-mindustry)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mindustry.yml)

## Docker Images
- `ich777/mindustry-server:${MINDUSTRY_VERSION:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MINDUSTRY_CONTAINER_NAME` |  | Container name |
| `MINDUSTRY_HOSTNAME` |  | Mindustry hostname |
| `MINDUSTRY_RESTART_POLICY` |  | Container restart policy |
| `MINDUSTRY_SRV_NAME` |  | Mindustry srv name |
| `MINDUSTRY_VERSION` |  | Mindustry version |
| `MINDUSTRY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |

## Configuration

### Volumes
- `./etc/games/${MINDUSTRY_HOSTNAME:-mindustry}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MINDUSTRY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MINDUSTRY_HOSTNAME:-mindustry}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable games-mindustry

# Configure environment variables (if needed)
make scaffold games-mindustry

# Start the service
make up
```
