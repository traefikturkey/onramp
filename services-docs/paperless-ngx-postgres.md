# Paperless Ngx Postgres

> paperless-ngx with postgres instead of mariadb

## Links
- [Official Repository](https://github.com/paperless-ngx/paperless-ngx)
- [Docker Image](https://hub.docker.com/r/linuxserver/paperless-ngx)
- [Official Documentation](https://docs.paperless-ngx.com/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/paperless-ngx-postgres.yml)

## Docker Images
- `docker.io/library/redis:${PAPERLESS_REDIS_TAG:-7}`
- `postgres:${PAPERLESS_POSTGRES_TAG:-13}`
- `docker.io/gotenberg/gotenberg:${PAPERLESS_GOTENBERG_TAG:-8}`
- `docker.io/apache/tika:latest`
- `ghcr.io/paperless-ngx/paperless-ngx:${PAPERLESS_NGX_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PAPERLESS_ADMINMAIL` |  | Paperless adminmail |
| `PAPERLESS_ADMINPASSWORD` |  | Service password |
| `PAPERLESS_ADMINUSER` |  | Service username |
| `PAPERLESS_DB_CONTAINER_NAME` |  | Container name |
| `PAPERLESS_DB_ENGINE` |  | Paperless db engine |
| `PAPERLESS_DB_HOST` |  | Paperless db host |
| `PAPERLESS_DB_NAME` |  | Paperless db name |
| `PAPERLESS_DB_PASS` |  | Paperless db pass |
| `PAPERLESS_DB_PORT` |  | Service port number |
| `PAPERLESS_DB_USER` |  | Service username |
| `PAPERLESS_GOTENBERG_TAG` |  | Paperless gotenberg tag |
| `PAPERLESS_MEM_LIMIT` |  | Paperless mem limit |
| `PAPERLESS_NGX_CONTAINER_NAME` |  | Container name |
| `PAPERLESS_NGX_DOCKER_TAG` |  | Docker image tag/version |
| `PAPERLESS_NGX_RESTART` |  | Container restart policy |
| `PAPERLESS_NGX_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PAPERLESS_POSTGRES_TAG` |  | Paperless postgres tag |
| `PAPERLESS_REDIS_TAG` |  | Paperless redis tag |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/paperless-ngx-postgres/redisdata:/data` - Data storage
- `./etc/paperless-ngx-postgres/pgdata:/var/lib/postgresql/data` - Data storage
- `./etc/paperless-ngx-postgres/data:/usr/src/paperless/data` - Data storage
- `./etc/paperless-ngx-postgres/media:/usr/src/paperless/media` - Volume mount
- `./etc/paperless-ngx-postgres/export:/usr/src/paperless/export` - Volume mount
- `./etc/paperless-ngx-postgres/consume:/usr/src/paperless/consume` - Volume mount
- `/etc/timezone:/etc/timezone` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.paperless-ngx-postgres.entrypoints=websecure`
- `traefik.http.routers.paperless-ngx-postgres.rule=Host(`${PAPERLESS_NGX_CONTAINER_NAME:-paperless}.${HOST_DOMAIN}`)`
- `traefik.http.services.paperless-ngx-postgres.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PAPERLESS_NGX_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PAPERLESS_NGX_CONTAINER_NAME:-paperless-ngx-postgres}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `broker`
- `db`
- `gotenberg`
- `tika`

## Quick Start

```bash
# Enable the service
make enable paperless-ngx-postgres

# Configure environment variables (if needed)
make scaffold paperless-ngx-postgres

# Start the service
make up
```

## Notes
- This service consists of 5 containers working together
- Requires broker, db, gotenberg, tika to be running
