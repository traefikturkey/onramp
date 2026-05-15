# Manyfold

> A self-hosted digital asset manager for 3d print files

## Links
- [Official Repository](https://github.com/manyfold3d/manyfold)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/manyfold.yml)

## Docker Images
- `ghcr.io/manyfold3d/manyfold:${MANYFOLD_DOCKER_TAG:-latest}`
- `postgres:15`
- `redis:7`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MANYFOLD_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `MANYFOLD_CONTAINER_NAME` |  | Container name |
| `MANYFOLD_DB_NAME` |  | Manyfold db name |
| `MANYFOLD_DB_PASSWORD` |  | Service password |
| `MANYFOLD_DB_USER` |  | Service username |
| `MANYFOLD_DOCKER_TAG` |  | Docker image tag/version |
| `MANYFOLD_HOST_NAME` |  | Manyfold host name |
| `MANYFOLD_MEM_LIMIT` |  | Manyfold mem limit |
| `MANYFOLD_RESTART` |  | Container restart policy |
| `MANYFOLD_SECRET_KEY_BASE` |  | Manyfold secret key base |
| `MANYFOLD_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `MANYFOLD_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/manyfold:/libraries` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/manyfold/db:/var/lib/postgresql/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${MANYFOLD_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.manyfold.entrypoints=websecure`
- `traefik.http.routers.manyfold.rule=Host(`${MANYFOLD_HOST_NAME:-manyfold}.${HOST_DOMAIN}`)`
- `traefik.http.services.manyfold.loadbalancer.server.port=3214`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MANYFOLD_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${MANYFOLD_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${MANYFOLD_HOST_NAME:-manyfold}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `manyfold-postgres`
- `manyfold-redis`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### manyfold-dedicated-postgres

**Purpose**: Rollback override for manyfold

**Changes**:
- **Adds/modifies services**: `manyfold`, `manyfold-postgres`
- **Adds/modifies environment variables**: `DATABASE_HOST`, `DATABASE_USER`, `DATABASE_PASSWORD`, `DATABASE_NAME`, `POSTGRES_USER`, `POSTGRES_PASSWORD`

**Usage**:
```bash
make enable-override manyfold-dedicated-postgres
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/manyfold-dedicated-postgres.yml)

### manyfold-dedicated-redis

**Purpose**: Rollback override for manyfold

**Changes**:
- **Adds/modifies services**: `manyfold`, `manyfold-redis`
- **Adds/modifies environment variables**: `REDIS_URL`

**Usage**:
```bash
make enable-override manyfold-dedicated-redis
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/manyfold-dedicated-redis.yml)

## Quick Start

```bash
# Enable the service
make enable manyfold

# Configure environment variables (if needed)
make scaffold manyfold

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires manyfold-postgres, manyfold-redis to be running
