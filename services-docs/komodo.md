# Komodo

> A web app to provide structure for managing your servers, builds, deployments, and automated procedures

## Links
- [Official Repository](https://github.com/moghtech/komodo)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/komodo.yml)

## Docker Images
- `postgres`
- `ghcr.io/ferretdb/ferretdb`
- `ghcr.io/mbecker20/komodo:${COMPOSE_KOMODO_IMAGE_TAG:-latest}`
- `ghcr.io/mbecker20/periphery:${COMPOSE_KOMODO_IMAGE_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COMPOSE_KOMODO_IMAGE_TAG` | latest | Compose komodo image tag |
| `COMPOSE_LOGGING_DRIVER` |  | Compose logging driver |
| `HOST_DOMAIN` |  | Host domain for service access |
| `KOMODO_CORE_CONTAINER_NAME` | komodo | Container name |
| `KOMODO_DATABASE_DB_NAME` | komodo | Komodo database db name |
| `KOMODO_DB_CONTAINER_NAME` | komodo-db | Container name |
| `KOMODO_DB_PASSWORD` | changeme | Service password |
| `KOMODO_DB_USERNAME` | komodo | Service username |
| `KOMODO_FERRET_CONTAINER_NAME` | komodo-ferretdb | Container name |
| `KOMODO_PERIPHERY_CONTAINER_NAME` | komodo-periphery | Container name |
| `KOMODO_WATCHTOWER_ENABLED` | false | Enable Watchtower auto-updates |
| `PERIPHERY_ROOT_DIRECTORY` | /apps/onramp/etc/komodo/periphery | Periphery root directory |

## Configuration

### Volumes
- `./etc/komodo/db:/var/lib/postgresql/data` - Volume mount
- `./etc/komodo/core:/repo-cache` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `/proc:/proc` - Volume mount
- `${PERIPHERY_ROOT_DIRECTORY}:${PERIPHERY_ROOT_DIRECTORY}` - Volume mount

### Networks
- `komodo-db`
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=false`
- `traefik.http.routers.komodo.entrypoints=websecure`
- `traefik.http.routers.komodo.rule=Host(`${KOMODO_CORE_CONTAINER_NAME:-komodo}.${HOST_DOMAIN}`)`
- `traefik.http.services.komodo.loadbalancer.server.port=9120`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KOMODO_WATCHTOWER_ENABLED:-false}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${KOMODO_CORE_CONTAINER_NAME:-komodo}.${HOST_DOMAIN}`
- `komodo.skip=true`

### Dependencies
This service depends on:
- `komodo-db`
- `komodo-ferretdb`

## Quick Start

```bash
# Enable the service
make enable komodo

# Configure environment variables (if needed)
make scaffold komodo

# Start the service
make up
```

## Notes
- This service consists of 4 containers working together
- Requires komodo-db, komodo-ferretdb to be running
