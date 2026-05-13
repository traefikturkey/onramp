# Sqliteweb

> Web-based SQLite Database Browser

## Links
- [Docker Image](https://hub.docker.com/r/tomdesinto/sqliteweb/)
- [Official Documentation](https://charlesleifer.com/blog/web-based-sqlite-database-browser-using-flask/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/sqliteweb.yml)

## Docker Images
- `tomdesinto/sqliteweb:${SQLITEWEB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SQLITEWEB_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `SQLITEWEB_CONTAINER_NAME` |  | Container name |
| `SQLITEWEB_DATABASE_FILE` |  | Sqliteweb database file |
| `SQLITEWEB_DATA_PATH` |  | Sqliteweb data path |
| `SQLITEWEB_DOCKER_TAG` |  | Docker image tag/version |
| `SQLITEWEB_RESTART` |  | Container restart policy |
| `SQLITEWEB_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `SQLITEWEB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${SQLITEWEB_DATA_PATH:-./media/databases/sqliteweb/}` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SQLITEWEB_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.sqliteweb.entrypoints=websecure`
- `traefik.http.routers.sqliteweb.rule=Host(`${SQLITEWEB_CONTAINER_NAME:-sqliteweb}.${HOST_DOMAIN}`)`
- `traefik.http.services.sqliteweb.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SQLITEWEB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${SQLITEWEB_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${SQLITEWEB_CONTAINER_NAME:-sqliteweb}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable sqliteweb

# Configure environment variables (if needed)
make scaffold sqliteweb

# Start the service
make up
```
