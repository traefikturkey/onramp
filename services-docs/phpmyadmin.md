# Phpmyadmin

> Web-based mysql and mariadb database management tool

## Links
- [Official Repository](https://github.com/phpmyadmin/docker)
- [Docker Image](https://hub.docker.com/r/phpmyadmin/phpmyadmin)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/phpmyadmin.yml)

## Docker Images
- `phpmyadmin/phpmyadmin:${PHPMYADMIN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PHPMYADMIN_DOCKER_TAG` |  | Docker image tag/version |
| `PHPMYADMIN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/phpmyadmin:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.phpmyadmin.entrypoints=websecure`
- `traefik.http.routers.phpmyadmin.rule=Host(`phpmyadmin.${HOST_DOMAIN}`)`
- `traefik.http.services.phpmyadmin.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PHPMYADMIN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=phpmyadmin.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable phpmyadmin

# Configure environment variables (if needed)
make scaffold phpmyadmin

# Start the service
make up
```
