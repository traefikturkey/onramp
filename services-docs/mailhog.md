# Mailhog

> Mail testing tool for developers

## Links
- [Official Repository](https://github.com/mailhog/MailHog)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mailhog.yml)

## Docker Images
- `mailhog/mailhog:${MAILHOG_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MAILHOG_CONTAINER_NAME` |  | Container name |
| `MAILHOG_DOCKER_TAG` |  | Docker image tag/version |
| `MAILHOG_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `MH_SMTP_BIND_ADDR` |  | Mh smtp bind addr |
| `MH_SMTP_PORT` |  | Service port number |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${MH_SMTP_PORT:-1025}:${MH_SMTP_PORT:-1025}`

### Volumes
- `mailhog_storage:/home/mailhog` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.mailhog.entrypoints=websecure`
- `traefik.http.routers.mailhog.rule=Host(`${MAILHOG_CONTAINER_NAME:-mailhog}.${HOST_DOMAIN}`)`
- `traefik.http.services.mailhog.loadbalancer.server.port=8025`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MAILHOG_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MAILHOG_CONTAINER_NAME:-mailhog}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable mailhog

# Configure environment variables (if needed)
make scaffold mailhog

# Start the service
make up
```
