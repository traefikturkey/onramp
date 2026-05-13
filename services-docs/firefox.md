# Firefox

> Runs mozilla firefox browser in a container

## Links
- [Official Repository](https://github.com/linuxserver/docker-firefox)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/firefox.yml)

## Docker Images
- `lscr.io/linuxserver/firefox:${FIREFOX_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FIREFOX_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `FIREFOX_CONTAINER_NAME` |  | Container name |
| `FIREFOX_DOCKER_TAG` |  | Docker image tag/version |
| `FIREFOX_PORT` |  | Service port number |
| `FIREFOX_RESTART` |  | Container restart policy |
| `FIREFOX_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `FIREFOX_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/firefox:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${FIREFOX_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.firefox.entrypoints=websecure`
- `traefik.http.routers.firefox.rule=Host(`${FIREFOX_CONTAINER_NAME:-firefox}.${HOST_DOMAIN}`)`
- `traefik.http.services.firefox.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FIREFOX_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${FIREFOX_AUTOHEAL:-true}`
- `joyride.host.name=${FIREFOX_CONTAINER_NAME:-firefox}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable firefox

# Configure environment variables (if needed)
make scaffold firefox

# Start the service
make up
```
