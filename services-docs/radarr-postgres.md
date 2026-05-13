# Radarr Postgres

> Container for running radarr with postgresql

## Links
- [Docker Image](https://hub.docker.com/_/postgres)
- [Official Documentation](https://wiki.servarr.com/radarr/postgres-setup)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/radarr-postgres.yml)

## Docker Images
- `postgres:14`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PGID` |  | Group ID for file permissions |
| `POSTGRES_DIR` |  | Postgres dir |
| `PUID` |  | User ID for file permissions |
| `RADARR_PG_USER` |  | Service username |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `5433:5432`

### Volumes
- `${POSTGRES_DIR:-./media/databases/radrr-postgres/data}` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=false`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable radarr-postgres

# Configure environment variables (if needed)
make scaffold radarr-postgres

# Start the service
make up
```
