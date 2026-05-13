# Kaizoku

> Web-based anime downloader

## Links
- [Official Repository](https://github.com/oae/kaizoku)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/kaizoku.yml)

## Docker Images
- `ghcr.io/oae/kaizoku:${KAIZOKU_DOCKER_TAG:-v1.6.1}`
- `redis:7-alpine`
- `postgres:alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KAIZOKU_CONTAINER_NAME` |  | Container name |
| `KAIZOKU_DB_VOLUME` |  | Kaizoku db volume |
| `KAIZOKU_DOCKER_TAG` |  | Docker image tag/version |
| `KAIZOKU_MANGA_VOLUME` |  | Kaizoku manga volume |
| `KAIZOKU_POSTGRES_DB` |  | PostgreSQL database name |
| `KAIZOKU_POSTGRES_PASSWORD` |  | Service password |
| `KAIZOKU_POSTGRES_USER` |  | Service username |
| `KAIZOKU_RESTART` |  | Container restart policy |
| `KAIZOKU_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `3000:3000`

### Volumes
- `${KAIZOKU_MANGA_VOLUME:-./media/manga}` - Volume mount
- `./etc/kaizoku/config:/config` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount
- `kaizoku-redis:/manga` - Volume mount
- `${KAIZOKU_DB_VOLUME:-./etc/kaizoku/db}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.kaizoku.entrypoints=websecure`
- `traefik.http.routers.kaizoku.middlewares=default-headers@file`
- `traefik.http.routers.kaizoku.rule=Host(`${KAIZOKU_CONTAINER_NAME:-kaizoku}.${HOST_DOMAIN}`)`
- `traefik.http.services.kaizoku.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KAIZOKU_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${KAIZOKU_CONTAINER_NAME:-kaizoku}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable kaizoku

# Configure environment variables (if needed)
make scaffold kaizoku

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
