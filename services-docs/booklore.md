# Booklore

> BookLore is a self-hosted web app for organizing and managing your personal book collection.

## Links
- [Official Repository](https://github.com/adityachandelgit/BookLore)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/booklore.yml)

## Docker Images
- `booklore/booklore:${BOOKLORE_DOCKER_TAG:-latest}`
- `lscr.io/linuxserver/mariadb:${BOOKLORE_MARIADB_TAG:-11.4.5}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BL_MYSQL_DATABASE` |  | Bl mysql database |
| `BL_MYSQL_PASSWORD` |  | Service password |
| `BL_MYSQL_ROOT_PASSWORD` |  | Service password |
| `BL_MYSQL_USER` |  | Service username |
| `BOOKLORE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `BOOKLORE_CONTAINER_NAME` |  | Container name |
| `BOOKLORE_DOCKER_TAG` |  | Docker image tag/version |
| `BOOKLORE_HOST_NAME` |  | Booklore host name |
| `BOOKLORE_MARIADB_TAG` |  | Booklore mariadb tag |
| `BOOKLORE_MEM_LIMIT` |  | Booklore mem limit |
| `BOOKLORE_RESTART` |  | Container restart policy |
| `BOOKLORE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `BOOKLORE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/booklore/data:/app/data` - Data storage
- `./media/books:/app/books` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/booklore/db:/config` - Volume mount

### Networks
- `traefik`
- `bl_int`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=${BOOKLORE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.booklore.entrypoints=websecure`
- `traefik.http.routers.booklore.rule=Host(`${BOOKLORE_HOST_NAME:-booklore}.${HOST_DOMAIN}`)`
- `traefik.http.services.booklore.loadbalancer.server.port=6060`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BOOKLORE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${BOOKLORE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${BOOKLORE_HOST_NAME:-booklore}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable booklore

# Configure environment variables (if needed)
make scaffold booklore

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
