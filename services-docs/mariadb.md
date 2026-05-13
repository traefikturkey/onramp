# Mariadb

> Shared MariaDB database server for multiple services

## Links
- [Docker Image](https://hub.docker.com/_/mariadb)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mariadb.yml)

## Docker Images
- `mariadb:${MARIADB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MARIADB_CONTAINER_NAME` |  | Container name |
| `MARIADB_DIR` |  | Mariadb dir |
| `MARIADB_DOCKER_TAG` |  | Docker image tag/version |
| `MARIADB_PASS` |  | Mariadb pass |
| `MARIADB_RESTART` |  | Container restart policy |
| `MARIADB_USER` |  | Service username |
| `MARIADB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `3306:3306`

### Volumes
- `${MARIADB_DIR:-./media/databases/mariadb/data}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MARIADB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MARIADB_CONTAINER_NAME:-mariadb}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable mariadb

# Configure environment variables (if needed)
make scaffold mariadb

# Start the service
make up
```
