# Kaneo

## Links
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/kaneo.yml)

## Docker Images
- `postgres:16-alpine`
- `ghcr.io/usekaneo/api:${KANEO_BACKEND_DOCKER_TAG:-latest}`
- `ghcr.io/usekaneo/web:${KANEO_FRONTEND_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KANEO_API_HOST_NAME` |  | Kaneo api host name |
| `KANEO_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `KANEO_BACKEND_CONTAINER_NAME` |  | Container name |
| `KANEO_BACKEND_DOCKER_TAG` |  | Docker image tag/version |
| `KANEO_FRONTEND_CONTAINER_NAME` |  | Container name |
| `KANEO_FRONTEND_DOCKER_TAG` |  | Docker image tag/version |
| `KANEO_HOST_NAME` |  | Kaneo host name |
| `KANEO_JWT_ACCESS` |  | Kaneo jwt access |
| `KANEO_POSTGRES_CONTAINER_NAME` |  | Container name |
| `KANEO_POSTGRES_DB` |  | PostgreSQL database name |
| `KANEO_POSTGRES_DIR` |  | Kaneo postgres dir |
| `KANEO_POSTGRES_PASSWORD` |  | Service password |
| `KANEO_POSTGRES_USER` |  | Service username |
| `KANEO_RESTART` |  | Container restart policy |
| `KANEO_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `KANEO_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `5432:5432`

### Volumes
- `${KANEO_POSTGRES_DIR:-./etc/kaneo/db}` - Volume mount

### Networks
- `kaneo_int`
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=${KANEO_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.kaneo-api.entrypoints=websecure`
- `traefik.http.routers.kaneo-api.rule=Host(`${KANEO_API_HOST_NAME:-kaneo-api}.${HOST_DOMAIN}`)`
- `traefik.http.routers.kaneo.entrypoints=websecure`
- `traefik.http.routers.kaneo.rule=Host(`${KANEO_HOST_NAME:-kaneo}.${HOST_DOMAIN}`)`
- `traefik.http.services.kaneo-api.loadbalancer.server.port=1337`
- `traefik.http.services.kaneo.loadbalancer.server.port=5173`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KANEO_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${KANEO_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${KANEO_HOST_NAME:-kaneo}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `kaneo-postgres`
- `kaneo-backend`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### kaneo-postgres

**Purpose**: Override to use dedicated PostgreSQL database for kaneo

**Changes**:
- **Adds/modifies services**: `kaneo-backend`, `kaneo-postgres`
- **Adds/modifies environment variables**: `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD`

**Usage**:
```bash
make enable-override kaneo-postgres
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/kaneo-postgres.yml)

## Quick Start

```bash
# Enable the service
make enable kaneo

# Configure environment variables (if needed)
make scaffold kaneo

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires kaneo-postgres, kaneo-backend to be running
