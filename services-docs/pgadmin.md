# Pgadmin

> Web-based postgresql administration tool

## Links
- [Docker Image](https://hub.docker.com/r/dpage/pgadmin4/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pgadmin.yml)

## Docker Images
- `dpage/pgadmin4:8.13`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGADMIN_CONTAINER_NAME` | pgadmin | Container name |
| `PGADMIN_DEFAULT_SERVER` | postgresql | Pgadmin default server |
| `PGADMIN_DOCKER_TAG` | 8.13 | Docker image tag/version |
| `PGADMIN_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PG_ADMIN_EMAIL` | admin@example.com | Pg admin email |
| `PG_ADMIN_PASSWORD` | changeme | Service password |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/pgadmin:/var/lib/pgadmin` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.pgadmin.entrypoints=websecure`
- `traefik.http.routers.pgadmin.rule=Host(`pgadmin.${HOST_DOMAIN}`)`
- `traefik.http.services.pgadmin.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PGADMIN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=pgadmin.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pgadmin

# Configure environment variables (if needed)
make scaffold pgadmin

# Start the service
make up
```
