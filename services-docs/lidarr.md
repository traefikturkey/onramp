# Lidarr

> Manages music collections and downloads

## Links
- [Official Repository](https://github.com/linuxserver/docker-lidarr)
- [Docker Image](https://hub.docker.com/r/linuxserver/lidarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/lidarr.yml)

## Docker Images
- `ghcr.io/hotio/lidarr:${LIDARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `LIDARR_CONTAINER_NAME` |  | Container name |
| `LIDARR_DOCKER_TAG` |  | Docker image tag/version |
| `LIDARR_DOWNLOADS_VOLUME` |  | Lidarr downloads volume |
| `LIDARR_MUSIC_VOLUME` |  | Lidarr music volume |
| `LIDARR_RESTART` |  | Container restart policy |
| `LIDARR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `8686:8686`

### Volumes
- `./etc/lidarr:/config` - Volume mount
- `${LIDARR_MUSIC_VOLUME:-./media/music}` - Volume mount
- `${LIDARR_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.lidarr.entrypoints=websecure`
- `traefik.http.routers.lidarr.rule=Host(`lidarr.${HOST_DOMAIN}`)`
- `traefik.http.services.lidarr.loadbalancer.server.port=8686`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LIDARR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=lidarr.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### lidarr-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `lidarr-nfs-media`, `lidarr-nfs-downloads`
- **Adds/modifies services**: `lidarr`

**Usage**:
```bash
make enable-override lidarr-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/lidarr-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable lidarr

# Configure environment variables (if needed)
make scaffold lidarr

# Start the service
make up
```
