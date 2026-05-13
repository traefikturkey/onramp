# Nextcloud

> Powerful self-hosted file sync and sharing platform

## Links
- [Official Repository](https://github.com/linuxserver/docker-nextcloud)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nextcloud.yml)

## Docker Images
- `lscr.io/linuxserver/nextcloud:${NEXTCLOUD_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NEXTCLOUD_CONTAINER_NAME` |  | Container name |
| `NEXTCLOUD_DATA_PATH` |  | Nextcloud data path |
| `NEXTCLOUD_DATA_VOLUME` |  | Nextcloud data volume |
| `NEXTCLOUD_DOCKER_TAG` |  | Docker image tag/version |
| `NEXTCLOUD_RESTART` |  | Container restart policy |
| `NEXTCLOUD_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/nextcloud:/config` - Volume mount
- `${NEXTCLOUD_DATA_VOLUME:-./media/nextcloud/}` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.nextcloud.entrypoints=websecure`
- `traefik.http.routers.nextcloud.rule=Host(`${NEXTCLOUD_CONTAINER_NAME:-nextcloud}.${HOST_DOMAIN}`)`
- `traefik.http.routers.nextcloud.service=nextcloud`
- `traefik.http.routers.nextcloud.tls=true`
- `traefik.http.services.nextcloud.loadbalancer.server.port=443`
- `traefik.http.services.nextcloud.loadbalancer.server.scheme=https`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NEXTCLOUD_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${NEXTCLOUD_CONTAINER_NAME:-nextcloud}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable nextcloud

# Configure environment variables (if needed)
make scaffold nextcloud

# Start the service
make up
```
