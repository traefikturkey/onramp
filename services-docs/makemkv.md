# Makemkv

> Fully automated container for MakeMKV with Web GUI

## Links
- [Official Repository](https://github.com/jlesage/docker-makemkv)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/makemkv.yml)

## Docker Images
- `jlesage/makemkv:${MAKEMKV_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MAKEMKV_AUTO_DISC_RIPPER` |  | Makemkv auto disc ripper |
| `MAKEMKV_AUTO_DISC_RIPPER_EJECT` |  | Makemkv auto disc ripper eject |
| `MAKEMKV_CONTAINER_NAME` |  | Container name |
| `MAKEMKV_DARK_MODE` |  | Makemkv dark mode |
| `MAKEMKV_DOCKER_TAG` |  | Docker image tag/version |
| `MAKEMKV_OPTICAL_DRIVE` |  | Makemkv optical drive |
| `MAKEMKV_OUTPUT_DIR` |  | Makemkv output dir |
| `MAKEMKV_RESTART` |  | Container restart policy |
| `MAKEMKV_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/makemkv:/config` - Volume mount
- `${MAKEMKV_OUTPUT_DIR:-./media/videos}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.makemkv.entrypoints=websecure`
- `traefik.http.routers.makemkv.rule=Host(`${MAKEMKV_CONTAINER_NAME:-makemkv}.${HOST_DOMAIN}`)`
- `traefik.http.services.makemkv.loadbalancer.server.port=5800`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MAKEMKV_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MAKEMKV_CONTAINER_NAME:-makemkv}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable makemkv

# Configure environment variables (if needed)
make scaffold makemkv

# Start the service
make up
```
