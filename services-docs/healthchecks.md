# Healthchecks

> Monitors cron jobs and sends alerts

## Links
- [Official Repository](https://github.com/linuxserver/docker-healthchecks)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/healthchecks.yml)

## Docker Images
- `lscr.io/linuxserver/healthchecks:${HEALTHCHECKS_DOCKER_TAG:-latest}`
- `postgres:${HEALTHCHECKS_DOCKER_TAG:-16.0}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HEALTHCHECKS_CONTAINER_NAME` |  | Container name |
| `HEALTHCHECKS_DB_NAME` |  | Healthchecks db name |
| `HEALTHCHECKS_DB_PASS` |  | Healthchecks db pass |
| `HEALTHCHECKS_DB_USER` |  | Service username |
| `HEALTHCHECKS_DOCKER_TAG` |  | Docker image tag/version |
| `HEALTHCHECKS_EMAIL` |  | Healthchecks email |
| `HEALTHCHECKS_RESTART` |  | Container restart policy |
| `HEALTHCHECKS_SECRET_KEY` |  | Healthchecks secret key |
| `HEALTHCHECKS_SITE_NAME` |  | Healthchecks site name |
| `HEALTHCHECKS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PUSHOVER_API_TOKEN` |  | Pushover api token |
| `PUSHOVER_SUBSCRIPTION_URL` |  | Pushover subscription url |

## Configuration

### Volumes
- `./etc/healthchecks:/var/lib/postgresql/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.healthchecks.entrypoints=websecure`
- `traefik.http.routers.healthchecks.middlewares=default-headers@file`
- `traefik.http.routers.healthchecks.rule=Host(`${HEALTHCHECKS_CONTAINER_NAME:-healthchecks}.${HOST_DOMAIN}`)`
- `traefik.http.services.healthchecks.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HEALTHCHECKS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${HEALTHCHECKS_CONTAINER_NAME:-healthchecks}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `hc-postgres`

## Quick Start

```bash
# Enable the service
make enable healthchecks

# Configure environment variables (if needed)
make scaffold healthchecks

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires hc-postgres to be running
