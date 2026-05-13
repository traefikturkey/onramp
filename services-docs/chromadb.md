# Chromadb

> open-source embedding database for LLM/AI applications

## Links
- [Official Repository](https://github.com/chroma-core/chroma/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/chromadb.yml)

## Docker Images
- `ghcr.io/chroma-core/chroma:${CHROMADB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CHROMADB_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `CHROMADB_CONTAINER_NAME` |  | Container name |
| `CHROMADB_DATA_PATH` |  | Chromadb data path |
| `CHROMADB_DOCKER_TAG` |  | Docker image tag/version |
| `CHROMADB_IS_PERSISTENT` |  | Chromadb is persistent |
| `CHROMADB_RESTART` |  | Container restart policy |
| `CHROMADB_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `CHROMADB_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${CHROMADB_DATA_PATH:-./media/databases/chromadb/}` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CHROMADB_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.chromadb.entrypoints=websecure`
- `traefik.http.routers.chromadb.rule=Host(`${CHROMADB_CONTAINER_NAME:-chromadb}.${HOST_DOMAIN}`)`
- `traefik.http.services.chromadb.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CHROMADB_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${CHROMADB_AUTOHEAL:-true}`
- `joyride.host.name=${CHROMADB_CONTAINER_NAME:-chromadb}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable chromadb

# Configure environment variables (if needed)
make scaffold chromadb

# Start the service
make up
```
