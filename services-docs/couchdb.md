# Couchdb

> CouchDB is a database that uses JSON for documents, an HTTP API, & JavaScript/declarative indexing

## Links
- [Docker Image](https://hub.docker.com/_/couchdb)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/couchdb.yml)

## Docker Images
- `couchdb:${COUCHDB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COUCHDB_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `COUCHDB_CONTAINER_NAME` |  | Container name |
| `COUCHDB_DOCKER_TAG` |  | Docker image tag/version |
| `COUCHDB_HOST_NAME` |  | Couchdb host name |
| `COUCHDB_MEM_LIMIT` |  | Couchdb mem limit |
| `COUCHDB_PASSWORD` |  | Service password |
| `COUCHDB_RESTART` |  | Container restart policy |
| `COUCHDB_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `COUCHDB_USER` |  | Service username |
| `COUCHDB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/couchdb/data:/opt/couchdb/data` - Data storage
- `./etc/couchdb/etc/local.d:/opt/couchdb/etc/local.d` - Volume mount
- `./etc/couchdb/docker-entrypoint.sh:/onramp-entrypoint.sh` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${COUCHDB_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.couchdb.entrypoints=websecure`
- `traefik.http.routers.couchdb.rule=Host(`${COUCHDB_HOST_NAME:-couchdb}.${HOST_DOMAIN}`)`
- `traefik.http.services.couchdb.loadbalancer.server.port=5984`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${COUCHDB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${COUCHDB_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${COUCHDB_HOST_NAME:-couchdb}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable couchdb

# Configure environment variables (if needed)
make scaffold couchdb

# Start the service
make up
```
