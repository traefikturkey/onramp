# Webtop

> Web-based desktop environment

## Links
- [Official Repository](https://github.com/linuxserver/docker-webtop)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/webtop.yml)

## Docker Images
- `lscr.io/linuxserver/webtop:${WEBTOP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WEBTOP_CONTAINER_NAME` |  | Container name |
| `WEBTOP_DOCKER_TAG` |  | Docker image tag/version |
| `WEBTOP_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/webtop:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.webtop.entrypoints=websecure`
- `traefik.http.routers.webtop.rule=Host(`${WEBTOP_CONTAINER_NAME:-webtop}.${HOST_DOMAIN}`)`
- `traefik.http.services.webtop.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WEBTOP_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WEBTOP_CONTAINER_NAME:-webtop}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable webtop

# Configure environment variables (if needed)
make scaffold webtop

# Start the service
make up
```
