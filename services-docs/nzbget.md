# Nzbget

> Binary newsgrabber for usenet

## Links
- [Official Repository](https://github.com/linuxserver/docker-nzbget)
- [Docker Image](https://hub.docker.com/r/linuxserver/nzbget)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nzbget.yml)

## Docker Images
- `lscr.io/linuxserver/nzbget:${NZBGET_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NZBGET_CONTAINER_NAME` |  | Container name |
| `NZBGET_DOCKER_TAG` |  | Docker image tag/version |
| `NZBGET_DOWNLOADS_DIR` |  | Nzbget downloads dir |
| `NZBGET_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/nzbget:/config` - Volume mount
- `${NZBGET_DOWNLOADS_DIR:-./media/downloads}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.nzbget.entrypoints=websecure`
- `traefik.http.routers.nzbget.rule=Host(`${NZBGET_CONTAINER_NAME:-nzbget}.${HOST_DOMAIN}`)`
- `traefik.http.services.nzbget.loadbalancer.server.port=6789`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NZBGET_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${NZBGET_CONTAINER_NAME:-nzbget}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable nzbget

# Configure environment variables (if needed)
make scaffold nzbget

# Start the service
make up
```
