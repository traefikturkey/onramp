# Wallabag

> Self-hosted read-it-later service

## Links
- [Official Repository](https://github.com/wallabag/wallabag)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wallabag.yml)

## Docker Images
- `wallabag/wallabag`
- `mariadb`
- `redis:alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `WALLABAG_CONTAINER_NAME` |  | Container name |
| `WALLABAG_DB_NAME` |  | Wallabag db name |
| `WALLABAG_DB_PASSWORD` |  | Service password |
| `WALLABAG_DB_ROOT_PASSWORD` |  | Service password |
| `WALLABAG_DB_USER` |  | Service username |
| `WALLABAG_EMAIL` |  | Wallabag email |
| `WALLABAG_SERVER_NAME` |  | Wallabag server name |
| `WALLABAG_SMTP_SERVER` |  | Wallabag smtp server |
| `WALLABAG_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/wallabag/images:/var/www/wallabag/web/assets/images` - Volume mount
- `./etc/wallabag/data:/var/lib/mysql` - Data storage

### Networks
- `traefik`
- `database`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.wallabag.entrypoints=websecure`
- `traefik.http.routers.wallabag.rule=Host(`${WALLABAG_CONTAINER_NAME:-wallabag}.${HOST_DOMAIN}`)`
- `traefik.http.services.wallabag.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WALLABAG_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WALLABAG_CONTAINER_NAME:-wallabag}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `db`
- `redis`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### wallabag-dedicated-mariadb

**Purpose**: Rollback override for wallabag

**Changes**:
- **Adds/modifies services**: `wallabag`, `db`
- **Adds/modifies environment variables**: `SYMFONY__ENV__DATABASE_HOST`, `MYSQL_ROOT_PASSWORD`

**Usage**:
```bash
make enable-override wallabag-dedicated-mariadb
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/wallabag-dedicated-mariadb.yml)

### wallabag-dedicated-redis

**Purpose**: Rollback override for wallabag

**Changes**:
- **Adds/modifies services**: `wallabag`, `redis`

**Usage**:
```bash
make enable-override wallabag-dedicated-redis
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/wallabag-dedicated-redis.yml)

### wallabag-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `wallabag-nfs-data`
- **Adds/modifies services**: `wallabag`

**Usage**:
```bash
make enable-override wallabag-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/wallabag-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable wallabag

# Configure environment variables (if needed)
make scaffold wallabag

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires db, redis to be running
