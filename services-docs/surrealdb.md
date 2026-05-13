# Surrealdb

> scalable, distributed, collaborative, document-graph database

## Links
- [Official Repository](https://github.com/surrealdb/surrealdb/blob/main/docker/DOCKER.md)
- [Official Documentation](https://surrealdb.com/docs/surrealdb/installation/running/docker)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/surrealdb.yml)

## Docker Images
- `surrealdb/surrealdb:${SURREALDB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `SURREALDB_AUTH` |  | Surrealdb auth |
| `SURREALDB_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `SURREALDB_CAPS_ALLOW_ALL` |  | Surrealdb caps allow all |
| `SURREALDB_CONTAINER_NAME` |  | Container name |
| `SURREALDB_DIR` |  | Surrealdb dir |
| `SURREALDB_DOCKER_TAG` |  | Docker image tag/version |
| `SURREALDB_LOG_LEVEL` |  | Surrealdb log level |
| `SURREALDB_NAME` |  | Surrealdb name |
| `SURREALDB_PASS` |  | Surrealdb pass |
| `SURREALDB_RESTART` |  | Container restart policy |
| `SURREALDB_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `SURREALDB_USER` |  | Service username |
| `SURREALDB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${SURREALDB_DIR:-./media/databases/surrealdb}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SURREALDB_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.surrealdb.entrypoints=websecure`
- `traefik.http.routers.surrealdb.rule=Host(`${SURREALDB_CONTAINER_NAME:-surrealdb}.${HOST_DOMAIN}`)`
- `traefik.http.services.surrealdb.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SURREALDB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${SURREALDB_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${SURREALDB_CONTAINER_NAME:-surrealdb}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable surrealdb

# Configure environment variables (if needed)
make scaffold surrealdb

# Start the service
make up
```
