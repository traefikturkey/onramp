# Iventoy

> ventoy as a PXE server (WARNING: This is a DHCP server!!!)

## Links
- [Official Repository](https://github.com/The-Drobe/iventoy-docker)
- [Docker Image](https://hub.docker.com/r/thedrobe/iventoy-docker)
- [Official Documentation](https://www.iventoy.com/en/index.html)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/iventoy.yml)

## Docker Images
- `thedrobe/iventoy-docker:${IVENTOY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `IVENTOY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `IVENTOY_CONTAINER_NAME` |  | Container name |
| `IVENTOY_DOCKER_TAG` |  | Docker image tag/version |
| `IVENTOY_ISO_PATH` |  | Iventoy iso path |
| `IVENTOY_RESTART` |  | Container restart policy |
| `IVENTOY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `IVENTOY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `16000:16000`
- `10809:10809`
- `67:67/udp`
- `69:69/udp`

### Volumes
- `${IVENTOY_ISO_PATH:-./media/isos}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${IVENTOY_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.iventoy.entrypoints=websecure`
- `traefik.http.routers.iventoy.rule=Host(`${IVENTOY_CONTAINER_NAME:-iventoy}.${HOST_DOMAIN}`)`
- `traefik.http.services.iventoy.loadbalancer.server.port=26000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${IVENTOY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${IVENTOY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${IVENTOY_CONTAINER_NAME:-iventoy}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable iventoy

# Configure environment variables (if needed)
make scaffold iventoy

# Start the service
make up
```
