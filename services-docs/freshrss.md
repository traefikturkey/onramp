# Freshrss

> Self-hosted rss feed reader

## Links
- [Official Repository](https://github.com/FreshRSS/FreshRSS)
- [Official Documentation](https://www.youtube.com/watch?v=nxV0CPNeFxY)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/freshrss.yml)

## Docker Images
- `lscr.io/linuxserver/freshrss:${FRESHRSS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FRESHRSS_CONTAINER_NAME` |  | Container name |
| `FRESHRSS_DOCKER_TAG` |  | Docker image tag/version |
| `FRESHRSS_RESTART` |  | Container restart policy |
| `FRESHRSS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/freshrss:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.freshrss.entrypoints=websecure`
- `traefik.http.routers.freshrss.rule=Host(`${FRESHRSS_CONTAINER_NAME:-freshrss}.${HOST_DOMAIN}`)`
- `traefik.http.services.freshrss.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FRESHRSS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FRESHRSS_CONTAINER_NAME:-freshrss}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable freshrss

# Configure environment variables (if needed)
make scaffold freshrss

# Start the service
make up
```
