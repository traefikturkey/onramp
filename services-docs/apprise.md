# Apprise

> Notification framework that supports various services

## Links
- [Official Repository](https://github.com/linuxserver/docker-apprise-api)
- [Docker Image](https://hub.docker.com/r/linuxserver/apprise-api)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/apprise.yml)

## Docker Images
- `lscr.io/linuxserver/apprise-api:${APPRISE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APPRISE_CONTAINER_NAME` |  | Container name |
| `APPRISE_DOCKER_TAG` |  | Docker image tag/version |
| `APPRISE_RESTART` |  | Container restart policy |
| `APPRISE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/apprise:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.apprise.entrypoints=websecure`
- `traefik.http.routers.apprise.rule=Host(`${APPRISE_CONTAINER_NAME:-apprise}.${HOST_DOMAIN}`)`
- `traefik.http.services.apprise.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${APPRISE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${APPRISE_CONTAINER_NAME:-apprise}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable apprise

# Configure environment variables (if needed)
make scaffold apprise

# Start the service
make up
```
