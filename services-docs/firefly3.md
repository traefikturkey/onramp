# Firefly3

> Manages personal finances and budgets

## Links
- [Official Repository](https://github.com/firefly-iii/firefly-iii/tree/main)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/firefly3.yml)

## Docker Images
- `fireflyiii/core:${FIREFLY3_DOCKER_TAG:-latest}`
- `mariadb`
- `alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FIREFLY3_CONTAINER_NAME` |  | Container name |
| `FIREFLY3_DOCKER_TAG` |  | Docker image tag/version |
| `FIREFLY3_RESTART` |  | Container restart policy |
| `FIREFLY3_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `FIREFLY_CRON_TOKEN` |  | Firefly cron token |
| `FIREFLY_DB_CONNECTION` |  | Firefly db connection |
| `FIREFLY_DB_CONTAINER_NAME` |  | Container name |
| `FIREFLY_DB_DATABASE` |  | Firefly db database |
| `FIREFLY_DB_HOST` |  | Firefly db host |
| `FIREFLY_DB_PASSWORD` |  | Service password |
| `FIREFLY_DB_PORT` |  | Service port number |
| `FIREFLY_DB_USERNAME` |  | Service username |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `82:8080`

### Volumes
- `firefly_upload:/var/www/html/storage/upload` - Uploaded files
- `/etc/localtime:/etc/localtime` - Volume mount
- `firefly_db:/var/lib/mysql` - Volume mount

### Networks
- `traefik`
- `firefly_iii`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=false`
- `traefik.http.routers.firefly3.entrypoints=websecure`
- `traefik.http.routers.firefly3.rule=Host(`${FIREFLY3_CONTAINER_NAME:-firefly}.${HOST_DOMAIN}`)`
- `traefik.http.services.firefly3.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FIREFLY3_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FIREFLY3_CONTAINER_NAME:-firefly}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `db`

## Quick Start

```bash
# Enable the service
make enable firefly3

# Configure environment variables (if needed)
make scaffold firefly3

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires db to be running
