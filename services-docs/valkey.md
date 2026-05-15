# Valkey

> Shared Valkey cache server for multiple services

## Links
- [Docker Image](https://hub.docker.com/r/valkey/valkey)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/valkey.yml)

## Docker Images
- `valkey/valkey:${VALKEY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `VALKEY_CONTAINER_NAME` |  | Container name |
| `VALKEY_DIR` |  | Valkey dir |
| `VALKEY_DOCKER_TAG` |  | Docker image tag/version |
| `VALKEY_RESTART` |  | Container restart policy |
| `VALKEY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `6379:6379`

### Volumes
- `${VALKEY_DIR:-./media/databases/valkey/data}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${VALKEY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${VALKEY_CONTAINER_NAME:-valkey}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable valkey

# Configure environment variables (if needed)
make scaffold valkey

# Start the service
make up
```
