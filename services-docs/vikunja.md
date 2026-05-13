# Vikunja

> Task and time management app

## Links
- [Official Documentation](https://vikunja.io/docs/full-docker-example/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/vikunja.yml)

## Docker Images
- `vikunja/vikunja:${VIKUNJA_DOCKER_TAG:-latest}`
- `mariadb:10`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `VIKUNJA_CONTAINER_NAME` |  | Container name |
| `VIKUNJA_DATABASE` |  | Vikunja database |
| `VIKUNJA_DATABASE_CONTAINER_NAME` |  | Container name |
| `VIKUNJA_DATABASE_HOST` |  | Vikunja database host |
| `VIKUNJA_DATABASE_PASSWORD` |  | Service password |
| `VIKUNJA_DATABASE_TYPE` |  | Vikunja database type |
| `VIKUNJA_DATABASE_USER` |  | Service username |
| `VIKUNJA_DOCKER_TAG` |  | Docker image tag/version |
| `VIKUNJA_FLAME_ICON` |  | Vikunja flame icon |
| `VIKUNJA_FLAME_NAME` |  | Vikunja flame name |
| `VIKUNJA_MYSQL_ROOT_PASSWORD` |  | Service password |
| `VIKUNJA_RESTART` |  | Container restart policy |
| `VIKUNJA_SERVICE_JWTSECRET` |  | Vikunja service jwtsecret |
| `VIKUNJA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/vikunja/db:/var/lib/mysql` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.vikunja.entrypoints=websecure`
- `traefik.http.routers.vikunja.rule=Host(`${VIKUNJA_CONTAINER_NAME:-vikunja}.${HOST_DOMAIN}`)`
- `traefik.http.services.vikunja.loadbalancer.server.port=3456`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${VIKUNJA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `flame.icon=${VIKUNJA_FLAME_ICON:-docker}`
- `flame.name=${VIKUNJA_FLAME_NAME:-vikunja}`
- `flame.type=application`
- `flame.url=https://${VIKUNJA_CONTAINER_NAME:-vikunja}.${HOST_DOMAIN}`
- `joyride.host.name=${VIKUNJA_CONTAINER_NAME:-vikunja}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable vikunja

# Configure environment variables (if needed)
make scaffold vikunja

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
