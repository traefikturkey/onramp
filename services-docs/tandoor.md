# Tandoor

> Recipe Management, meal-planning, shopping lists

## Links
- [Official Repository](https://github.com/TandoorRecipes/recipes)
- [Official Documentation](https://tandoor.dev/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/tandoor.yml)

## Docker Images
- `postgres:16-alpine`
- `vabene1111/recipes:${TANDOOR_DOCKER_TAG:-latest}`
- `nginx:mainline-alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TANDOORDB_CONTAINER_NAME` |  | Container name |
| `TANDOOR_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `TANDOOR_CONTAINER_NAME` |  | Container name |
| `TANDOOR_DB_ENGINE` |  | Tandoor db engine |
| `TANDOOR_DOCKER_TAG` |  | Docker image tag/version |
| `TANDOOR_HOST_NAME` |  | Tandoor host name |
| `TANDOOR_POSTGRES_DB` |  | PostgreSQL database name |
| `TANDOOR_POSTGRES_HOST` |  | Tandoor postgres host |
| `TANDOOR_POSTGRES_PASSWORD` |  | Service password |
| `TANDOOR_POSTGRES_PORT` |  | Service port number |
| `TANDOOR_POSTGRES_USER` |  | Service username |
| `TANDOOR_RESTART` |  | Container restart policy |
| `TANDOOR_SECRET_KEY` |  | Tandoor secret key |
| `TANDOOR_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `TANDOOR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/tandoor/db:/var/lib/postgresql/data` - Volume mount
- `./etc/tandoor/static:/opt/recipes/staticfiles` - Volume mount
- `./etc/tandoor/media:/opt/recipes/mediafiles` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/tandoor/nginx:/etc/nginx/conf.d` - Volume mount
- `./etc/tandoor/static:/opt/recipes/staticfiles` - Volume mount
- `./etc/tandoor/media:/media` - Volume mount

### Networks
- `tandoor-int`
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=${TANDOOR_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.tandoor.entrypoints=websecure`
- `traefik.http.routers.tandoor.rule=Host(`${TANDOOR_HOST_NAME:-recipe}.${HOST_DOMAIN}`)`
- `traefik.http.services.tandoor.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TANDOOR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${TANDOOR_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${TANDOOR_HOST_NAME:-recipe}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `tandoor-db`
- `tandoor-web`

## Quick Start

```bash
# Enable the service
make enable tandoor

# Configure environment variables (if needed)
make scaffold tandoor

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires tandoor-db, tandoor-web to be running
