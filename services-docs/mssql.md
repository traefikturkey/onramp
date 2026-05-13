# Mssql

> Microsoft sql server container

## Links
- [Official Repository](https://github.com/microsoft/mssql-docker)
- [Docker Image](https://hub.docker.com/_/microsoft-mssql-server)
- [Official Documentation](https://docs.microsoft.com/en-us/sql/linux/sql-server-linux-overview?view=sql-server-ver16)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mssql.yml)

## Docker Images
- `mcr.microsoft.com/mssql/server:${MSSQL_DOCKER_TAG:-2022-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MSSQL_DB_DIR` |  | Mssql db dir |
| `MSSQL_DOCKER_TAG` |  | Docker image tag/version |
| `MSSQL_SA_PASSWORD` |  | Service password |
| `MSSQL_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `1433:1433`

### Volumes
- `${MSSQL_DB_DIR:-./media/databases/mssql}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MSSQL_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=mssql.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable mssql

# Configure environment variables (if needed)
make scaffold mssql

# Start the service
make up
```
