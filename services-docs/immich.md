# Immich

> Container for running immich, a self-hosted Google Photos alternative.

## Links
- [Official Documentation](https://immich.app/docs/install/environment-variables)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/immich.yml)

## Docker Images
- `ghcr.io/immich-app/immich-server:${IMMICH_VERSION:-v2.0.1}`
- `ghcr.io/immich-app/immich-machine-learning:${IMMICH_VERSION:-v2.0.1}`
- `docker.io/valkey/valkey:8-bookworm@sha256:fea8b3e67b15729d4bb70589eb03367bab9ad1ee89c876f54327fc7c6e618571`
- `ghcr.io/immich-app/postgres:14-vectorchord0.4.3-pgvectors0.2.0@sha256:41eacbe83eca995561fe43814fd4891e16e39632806253848efaf04d3c8a8b84`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `IMMICH_BACKUP_RETENTION` |  | Immich backup retention |
| `IMMICH_BACKUP_SCHEDULE` |  | Immich backup schedule |
| `IMMICH_CONTAINER_NAME` |  | Container name |
| `IMMICH_DB_HOSTNAME` |  | Database host address |
| `IMMICH_MODEL_CACHE_DIR` |  | Immich model cache dir |
| `IMMICH_POSTGRES_DB` |  | PostgreSQL database name |
| `IMMICH_POSTGRES_DB_BACKUP_DIR` |  | PostgreSQL database name |
| `IMMICH_POSTGRES_DB_DIR` |  | PostgreSQL database name |
| `IMMICH_POSTGRES_PASSWORD` |  | Service password |
| `IMMICH_POSTGRES_USER` |  | Service username |
| `IMMICH_REDIS_CONTAINER_NAME` |  | Container name |
| `IMMICH_RESTART_POLICY` |  | Container restart policy |
| `IMMICH_TYPESENSE_API_KEY` |  | Immich typesense api key |
| `IMMICH_UPLOAD_LOCATION` |  | Directory for uploaded files |
| `IMMICH_VERSION` |  | Immich version |
| `IMMICH_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |

## Configuration

### Volumes
- `${IMMICH_UPLOAD_LOCATION:-./etc/immich/upload}` - Uploaded files
- `/etc/localtime:/etc/localtime` - Volume mount
- `${IMMICH_MODEL_CACHE_DIR:-./etc/immich/model-cache}` - Volume mount
- `${IMMICH_POSTGRES_DB_DIR:-./etc/immich/db}` - Volume mount

### Networks
- `traefik`
- `immich-db`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=true`
- `traefik.http.routers.immich.entrypoints=websecure`
- `traefik.http.routers.immich.rule=Host(`${IMMICH_CONTAINER_NAME:-immich}.${HOST_DOMAIN}`)`
- `traefik.http.services.immich.loadbalancer.server.port=2283`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${IMMICH_WATCHTOWER_ENABLED:-false}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${IMMICH_CONTAINER_NAME:-immich}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `redis`
- `database`

## Quick Start

```bash
# Enable the service
make enable immich

# Configure environment variables (if needed)
make scaffold immich

# Start the service
make up
```

## Notes
- This service consists of 4 containers working together
- Requires redis, database to be running
