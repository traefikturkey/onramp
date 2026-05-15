# Geopulse

> A self-hosted location tracking and analysis platform

## Links
- [Official Repository](https://github.com/tess1o/geopulse)
- [Official Documentation](https://tess1o.github.io/geopulse/docs/getting-started/introduction)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/geopulse.yml)

## Docker Images
- `postgis/postgis:17-3.5`
- `ghcr.io/tess1o/geopulse-backend:${GEOPULSE_DOCKER_TAG:-native-latest}`
- `ghcr.io/tess1o/geopulse-ui:${GEOPULSE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GEOPULSE_AUTH_OIDC_REGISTRATION_ENABLED` |  | Geopulse auth oidc registration enabled |
| `GEOPULSE_AUTH_PASSWORD_REGISTRATION_ENABLED` |  | Service password |
| `GEOPULSE_AUTH_REGISTRATION_ENABLED` |  | Geopulse auth registration enabled |
| `GEOPULSE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `GEOPULSE_CONTAINER_NAME` |  | Container name |
| `GEOPULSE_DOCKER_TAG` |  | Docker image tag/version |
| `GEOPULSE_HOST_NAME` |  | Geopulse host name |
| `GEOPULSE_MEM_LIMIT` |  | Geopulse mem limit |
| `GEOPULSE_OIDC_ENABLED` |  | Geopulse oidc enabled |
| `GEOPULSE_OIDC_PROVIDER_GENERIC_CLIENT_ID` |  | Geopulse oidc provider generic client id |
| `GEOPULSE_OIDC_PROVIDER_GENERIC_CLIENT_SECRET` |  | Geopulse oidc provider generic client secret |
| `GEOPULSE_OIDC_PROVIDER_GENERIC_DISCOVERY_URL` |  | Geopulse oidc provider generic discovery url |
| `GEOPULSE_OIDC_PROVIDER_GENERIC_ENABLED` |  | Geopulse oidc provider generic enabled |
| `GEOPULSE_OIDC_PROVIDER_GENERIC_NAME` |  | Geopulse oidc provider generic name |
| `GEOPULSE_OIDC_PROVIDER_GOOGLE_CLIENT_ID` |  | Geopulse oidc provider google client id |
| `GEOPULSE_OIDC_PROVIDER_GOOGLE_CLIENT_SECRET` |  | Geopulse oidc provider google client secret |
| `GEOPULSE_OIDC_PROVIDER_GOOGLE_DISCOVERY_URL` |  | Geopulse oidc provider google discovery url |
| `GEOPULSE_OIDC_PROVIDER_GOOGLE_ENABLED` |  | Geopulse oidc provider google enabled |
| `GEOPULSE_POSTGRES_AUTOVACUUM_NAPTIME` |  | Geopulse postgres autovacuum naptime |
| `GEOPULSE_POSTGRES_CHECKPOINT_TARGET` |  | Geopulse postgres checkpoint target |
| `GEOPULSE_POSTGRES_DB` |  | PostgreSQL database name |
| `GEOPULSE_POSTGRES_EFFECTIVE_CACHE_SIZE` |  | Geopulse postgres effective cache size |
| `GEOPULSE_POSTGRES_HOST` |  | Geopulse postgres host |
| `GEOPULSE_POSTGRES_IO_CONCURRENCY` |  | Geopulse postgres io concurrency |
| `GEOPULSE_POSTGRES_LOG_SLOW_QUERIES` |  | Geopulse postgres log slow queries |
| `GEOPULSE_POSTGRES_MAINTENANCE_WORK_MEM` |  | Geopulse postgres maintenance work mem |
| `GEOPULSE_POSTGRES_MAX_WAL_SIZE` |  | Geopulse postgres max wal size |
| `GEOPULSE_POSTGRES_PASSWORD` |  | Service password |
| `GEOPULSE_POSTGRES_PORT` |  | Service port number |
| `GEOPULSE_POSTGRES_RANDOM_PAGE_COST` |  | Geopulse postgres random page cost |
| `GEOPULSE_POSTGRES_SHARED_BUFFERS` |  | Geopulse postgres shared buffers |
| `GEOPULSE_POSTGRES_USERNAME` |  | Service username |
| `GEOPULSE_POSTGRES_VACUUM_SCALE_FACTOR` |  | Geopulse postgres vacuum scale factor |
| `GEOPULSE_POSTGRES_WAL_BUFFERS` |  | Geopulse postgres wal buffers |
| `GEOPULSE_POSTGRES_WORK_MEM` |  | Geopulse postgres work mem |
| `GEOPULSE_RESTART` |  | Container restart policy |
| `GEOPULSE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `GEOPULSE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/geopulse/postgres:/var/lib/postgresql/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/geopulse/keys:/app/keys` - Volume mount
- `./etc/geopulse/nginx/default.conf:/etc/nginx/conf.d/default.conf` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${GEOPULSE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.geopulse.entrypoints=websecure`
- `traefik.http.routers.geopulse.rule=Host(`${GEOPULSE_HOST_NAME:-geopulse}.${HOST_DOMAIN}`)`
- `traefik.http.services.geopulse.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GEOPULSE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${GEOPULSE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${GEOPULSE_HOST_NAME:-geopulse}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable geopulse

# Configure environment variables (if needed)
make scaffold geopulse

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
