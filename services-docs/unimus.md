# Unimus

> contianer for multi-vendor network device configuration backup and management solution

## Links
- [Official Repository](https://github.com/crocandr/docker-unimus)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/unimus.yml)

## Docker Images
- `croc/unimus:${UNIMUS_VERSION:-latest}`
- `mariadb:10`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `UNIMUSDB_RESTART_POLICY` |  | Container restart policy |
| `UNIMUS_CONTAINER_NAME` |  | Container name |
| `UNIMUS_MYSQL_DB` |  | Unimus mysql db |
| `UNIMUS_MYSQL_ROOT_PASSWORD` |  | Service password |
| `UNIMUS_MYSQL_USER` |  | Service username |
| `UNIMUS_POSTGRES_USER` |  | Service username |
| `UNIMUS_RESTART_POLICY` |  | Container restart policy |
| `UNIMUS_VERSION` |  | Unimus version |
| `UNIMUS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/unimus/web:/etc/unimus` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/unimus/db:/var/lib/mysql` - Volume mount

### Networks
- `traefik`
- `unimus-dbnet`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=false`
- `traefik.http.routers.unimus.entrypoints=websecure`
- `traefik.http.routers.unimus.rule=Host(`${UNIMUS_CONTAINER_NAME:-unimus}.${HOST_DOMAIN}`)`
- `traefik.http.services.unimus.loadbalancer.server.port=8085`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${UNIMUS_WATCHTOWER_ENABLED:-false}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${UNIMUS_CONTAINER_NAME:-unimus}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `unimus-database`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### unimus-dedicated-mariadb

**Purpose**: Rollback override for unimus

**Changes**:
- **Adds/modifies services**: `unimus-app`, `unimus-database`
- **Adds/modifies environment variables**: `POSTGRES_USER`, `MYSQL_ROOT_PASSWORD`, `MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`

**Usage**:
```bash
make enable-override unimus-dedicated-mariadb
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/unimus-dedicated-mariadb.yml)

## Quick Start

```bash
# Enable the service
make enable unimus

# Configure environment variables (if needed)
make scaffold unimus

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires unimus-database to be running
