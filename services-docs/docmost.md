# Docmost

> Docmost is an open-source collaborative wiki and documentation software.

## Links
- [Official Repository](https://github.com/docmost/docmost)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/docmost.yml)

## Docker Images
- `docmost/docmost:${DOCMOST_DOCKER_TAG:-latest}`
- `postgres:16-alpine`
- `redis:7.2-alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCMOST_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DOCMOST_CONTAINER_NAME` |  | Container name |
| `DOCMOST_DB_CONTAINER_NAME` |  | Container name |
| `DOCMOST_DOCKER_TAG` |  | Docker image tag/version |
| `DOCMOST_MEM_LIMIT` |  | Docmost mem limit |
| `DOCMOST_POSTGRES_DB` |  | PostgreSQL database name |
| `DOCMOST_POSTGRES_PASSWORD` |  | Service password |
| `DOCMOST_POSTGRES_USER` |  | Service username |
| `DOCMOST_REDIS_CONTAINER_NAME` |  | Container name |
| `DOCMOST_RESTART` |  | Container restart policy |
| `DOCMOST_SECRET` |  | Docmost secret |
| `DOCMOST_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `DOCMOST_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/docmost/app:/app/data/storage` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/docmost/db:/var/lib/postgresql/data` - Volume mount
- `./etc/docmost/redis:/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DOCMOST_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.docmost.entrypoints=websecure`
- `traefik.http.routers.docmost.rule=Host(`${DOCMOST_CONTAINER_NAME:-docmost}.${HOST_DOMAIN}`)`
- `traefik.http.services.docmost.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCMOST_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DOCMOST_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${DOCMOST_CONTAINER_NAME:-docmost}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `docmost-db`
- `docmost-redis`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### docmost-dedicated-postgres

**Purpose**: Rollback override for docmost

**Changes**:
- **Adds/modifies services**: `docmost`, `docmost-db`
- **Adds/modifies environment variables**: `DATABASE_URL`, `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

**Usage**:
```bash
make enable-override docmost-dedicated-postgres
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/docmost-dedicated-postgres.yml)

### docmost-dedicated-redis

**Purpose**: Rollback override for docmost

**Changes**:
- **Adds/modifies services**: `docmost`, `docmost-redis`
- **Adds/modifies environment variables**: `REDIS_URL`

**Usage**:
```bash
make enable-override docmost-dedicated-redis
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/docmost-dedicated-redis.yml)

## Quick Start

```bash
# Enable the service
make enable docmost

# Configure environment variables (if needed)
make scaffold docmost

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires docmost-db, docmost-redis to be running
