# Dawarich

> Self-hostable alternative to Google Location History (Google Maps Timeline)

## Links
- [Official Repository](https://github.com/Freika/dawarich)
- [Official Documentation](https://dawarich.app/docs/intro)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dawarich.yml)

## Docker Images
- `freikin/dawarich:${DAWARICH_DOCKER_TAG:-latest}`
- `postgis/postgis:17-3.5-alpine`
- `redis:7.4-alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DAWARICH_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DAWARICH_CONTAINER_NAME` |  | Container name |
| `DAWARICH_DISTANCE_UNIT` |  | Dawarich distance unit |
| `DAWARICH_DOCKER_TAG` |  | Docker image tag/version |
| `DAWARICH_HOST_NAME` |  | Dawarich host name |
| `DAWARICH_MIN_MINS` |  | Dawarich min mins |
| `DAWARICH_POSTGRES_PW` |  | Dawarich postgres pw |
| `DAWARICH_POSTGRES_USER` |  | Service username |
| `DAWARICH_RESTART` |  | Container restart policy |
| `DAWARICH_SECRET_KEY_BASE` |  | Dawarich secret key base |
| `DAWARICH_SMTP_DOMAIN` |  | Dawarich smtp domain |
| `DAWARICH_SMTP_FROM` |  | Dawarich smtp from |
| `DAWARICH_SMTP_PASSWORD` |  | Service password |
| `DAWARICH_SMTP_PORT` |  | Service port number |
| `DAWARICH_SMTP_SERVER` |  | Dawarich smtp server |
| `DAWARICH_SMTP_USERNAME` |  | Service username |
| `DAWARICH_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `DAWARICH_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/dawrich/storage:/var/app/storage` - Volume mount
- `./etc/dawarich/public:/var/app/public` - Volume mount
- `./etc/dawarich/watched:/var/app/tmp/imports/watched` - Volume mount
- `./etc/dawarich/db:/var/lib/postgresql/data` - Volume mount
- `./etc/dawarich/redis:/var/shared/redis` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DAWARICH_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.dawarich.entrypoints=websecure`
- `traefik.http.routers.dawarich.rule=Host(`${DAWARICH_HOST_NAME:-dawarich}.${HOST_DOMAIN}`)`
- `traefik.http.services.dawarich.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DAWARICH_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DAWARICH_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${DAWARICH_HOST_NAME:-dawarich}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### dawarich-dedicated-redis

**Purpose**: Rollback override for dawarich

**Changes**:
- **Adds/modifies services**: `dawarich`, `dawarich_sidekiq`, `dawarich_redis`
- **Adds/modifies environment variables**: `REDIS_URL`

**Usage**:
```bash
make enable-override dawarich-dedicated-redis
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/dawarich-dedicated-redis.yml)

## Quick Start

```bash
# Enable the service
make enable dawarich

# Configure environment variables (if needed)
make scaffold dawarich

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
