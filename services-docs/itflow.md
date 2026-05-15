# Itflow

> IT documentation, ticketing and accounting system.

## Links
- [Official Documentation](https://itflow.org/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/itflow.yml)

## Docker Images
- `mariadb:10.6.11`
- `lued/itflow:${ITFLOW_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `ITFLOW_CONTAINER_NAME` |  | Container name |
| `ITFLOW_DB_NAME` |  | Itflow db name |
| `ITFLOW_DB_PASS` |  | Itflow db pass |
| `ITFLOW_DB_USER` |  | Service username |
| `ITFLOW_DOCKER_TAG` |  | Docker image tag/version |
| `ITFLOW_HOSTNAME` |  | Itflow hostname |
| `ITFLOW_RESTART` |  | Container restart policy |
| `ITFLOW_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/itflow/data:/var/lib/mysql/` - Data storage
- `./etc/itflow/www:/var/www/html` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.itflow.entrypoints=websecure`
- `traefik.http.routers.itflow.rule=Host(`${ITFLOW_CONTAINER_NAME:-itflow}.${HOST_DOMAIN}`)`
- `traefik.http.services.itflow.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ITFLOW_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${ITFLOW_CONTAINER_NAME:-itflow}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `itflow-db`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### itflow-dedicated-mariadb

**Purpose**: Rollback override for itflow

**Changes**:
- **Adds/modifies services**: `itflow`, `itflow-db`
- **Adds/modifies environment variables**: `ITFLOW_DB_HOST`, `MARIADB_RANDOM_ROOT_PASSWORD`, `MARIADB_DATABASE`, `MARIADB_USER`, `MARIADB_PASSWORD`

**Usage**:
```bash
make enable-override itflow-dedicated-mariadb
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/itflow-dedicated-mariadb.yml)

## Quick Start

```bash
# Enable the service
make enable itflow

# Configure environment variables (if needed)
make scaffold itflow

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires itflow-db to be running
