# Joplin

> Note-taking and to-do app

## Links
- [Official Repository](https://github.com/laurent22/joplin)
- [Docker Image](https://hub.docker.com/r/joplin/server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/joplin.yml)

## Docker Images
- `postgres:15`
- `joplin/server:${JOPLIN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `JOPLIN_CONTAINER_NAME` |  | Container name |
| `JOPLIN_DB_CONTAINER_NAME` |  | Container name |
| `JOPLIN_DOCKER_TAG` |  | Docker image tag/version |
| `JOPLIN_POSTGRES_DATABASE` |  | Joplin postgres database |
| `JOPLIN_POSTGRES_PASSWORD` |  | Service password |
| `JOPLIN_POSTGRES_PORT` |  | Service port number |
| `JOPLIN_POSTGRES_USER` |  | Service username |
| `JOPLIN_RESTART` |  | Container restart policy |
| `JOPLIN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `5432:5432`

### Volumes
- `./etc/joplin:/var/lib/postgresql/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.joplin.entrypoints=websecure`
- `traefik.http.routers.joplin.rule=Host(`${JOPLIN_CONTAINER_NAME:-joplin}.${HOST_DOMAIN}`)`
- `traefik.http.services.joplin.loadbalancer.server.port=22300`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${JOPLIN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${JOPLIN_CONTAINER_NAME:-joplin}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `db`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### joplin-api-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `joplin-api-nfs-data`
- **Adds/modifies services**: `joplin-api`

**Usage**:
```bash
make enable-override joplin-api-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/joplin-api-nfs.yml)

### joplin-dedicated-postgres

**Purpose**: Rollback override for joplin

**Changes**:
- **Adds/modifies services**: `joplin`, `joplin-db`
- **Adds/modifies environment variables**: `POSTGRES_HOST`, `POSTGRES_PASSWORD`, `POSTGRES_USER`, `POSTGRES_DATABASE`, `POSTGRES_DB`

**Usage**:
```bash
make enable-override joplin-dedicated-postgres
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/joplin-dedicated-postgres.yml)

## Quick Start

```bash
# Enable the service
make enable joplin

# Configure environment variables (if needed)
make scaffold joplin

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires db to be running
