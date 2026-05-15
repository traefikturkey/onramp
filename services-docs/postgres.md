# Postgres

> Shared PostgreSQL database server for multiple services

## Links
- [Docker Image](https://hub.docker.com/_/postgres)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/postgres.yml)

## Docker Images
- `postgres:${POSTGRES_DOCKER_TAG:-16}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PG_DB` |  | Pg db |
| `PG_MAX_CONNECTIONS` |  | Pg max connections |
| `PG_USER` |  | Service username |
| `PG_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `POSTGRES_CONTAINER_NAME` |  | Container name |
| `POSTGRES_DIR` |  | Postgres dir |
| `POSTGRES_DOCKER_TAG` |  | Docker image tag/version |
| `POSTGRES_RESTART` |  | Container restart policy |
| `POSTGRES_USER` |  | PostgreSQL database username |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `5432:5432`

### Volumes
- `${POSTGRES_DIR:-./media/databases/postgres/data}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PG_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${POSTGRES_CONTAINER_NAME:-postgres}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable postgres

# Configure environment variables (if needed)
make scaffold postgres

# Start the service
make up
```
