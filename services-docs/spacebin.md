# Spacebin

> spacebin: text sharing for the final frontier (Pastebin alternative)

## Links
- [Official Repository](https://github.com/lukewhrit/spacebin)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/spacebin.yml)

## Docker Images
- `spacebinorg/spirit:${SPACEBIN_DOCKER_TAG:-latest}`
- `postgres:16.3-alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SPACEBIN_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `SPACEBIN_CONNECTION_URI` |  | Spacebin connection uri |
| `SPACEBIN_CONTAINER_NAME` |  | Container name |
| `SPACEBIN_DOCKER_TAG` |  | Docker image tag/version |
| `SPACEBIN_EXPIRATION_IN_DAYS` |  | Spacebin expiration in days |
| `SPACEBIN_HOST_NAME` |  | Spacebin host name |
| `SPACEBIN_ID_LENGTH` |  | Spacebin id length |
| `SPACEBIN_ID_TYPE` |  | Spacebin id type |
| `SPACEBIN_MEM_LIMIT` |  | Spacebin mem limit |
| `SPACEBIN_POSTGRES_DB` |  | PostgreSQL database name |
| `SPACEBIN_POSTGRES_PASSWORD` |  | Service password |
| `SPACEBIN_POSTGRES_USER` |  | Service username |
| `SPACEBIN_RATELIMITER` |  | Spacebin ratelimiter |
| `SPACEBIN_RESTART` |  | Container restart policy |
| `SPACEBIN_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `SPACEBIN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/spacebin/db:/var/lib/postgresql/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SPACEBIN_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.spacebin.entrypoints=websecure`
- `traefik.http.routers.spacebin.middlewares=default-headers@file`
- `traefik.http.routers.spacebin.rule=Host(`${SPACEBIN_HOST_NAME:-spacebin}.${HOST_DOMAIN}`)`
- `traefik.http.services.spacebin.loadbalancer.server.port=9000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SPACEBIN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${SPACEBIN_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${SPACEBIN_HOST_NAME:-spacebin}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### spacebin-dedicated-postgres

**Purpose**: Rollback override for spacebin

**Changes**:
- **Adds/modifies services**: `spacebin`, `spacebin-db`
- **Adds/modifies environment variables**: `SPIRIT_CONNECTION_URI`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`

**Usage**:
```bash
make enable-override spacebin-dedicated-postgres
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/spacebin-dedicated-postgres.yml)

## Quick Start

```bash
# Enable the service
make enable spacebin

# Configure environment variables (if needed)
make scaffold spacebin

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
