# Radarr

> Manages movie collections and downloads

## Links
- [Official Repository](https://github.com/linuxserver/docker-radarr)
- [Docker Image](https://hub.docker.com/r/linuxserver/radarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/radarr.yml)

## Docker Images
- `lscr.io/linuxserver/radarr:${RADARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MEDIA_DOWNLOADS_VOLUME` | ./media/downloads | Media downloads volume |
| `MEDIA_MOVIES_VOLUME` | ./media/movies | Media movies volume |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `RADARR_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `RADARR_CONTAINER_NAME` | radarr | Container name |
| `RADARR_DOCKER_TAG` | latest | Docker image tag/version |
| `RADARR_RESTART` | unless-stopped | Container restart policy |
| `RADARR_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `RADARR_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `7878:7878`

### Volumes
- `./etc/radarr:/config` - Volume mount
- `./etc/radarr/custom-services.d:/custom-services.d` - Volume mount
- `./etc/radarr/custom-cont-init.d:/custom-cont-init.d` - Volume mount
- `${MEDIA_MOVIES_VOLUME:-./media/movies}` - Volume mount
- `${MEDIA_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount
- `/dev/rtc:/dev/rtc` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${RADARR_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.radarr.entrypoints=websecure`
- `traefik.http.routers.radarr.rule=Host(`${RADARR_CONTAINER_NAME:-radarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.radarr.loadbalancer.server.port=7878`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${RADARR_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${RADARR_AUTOHEAL:-true}`
- `joyride.host.name=${RADARR_CONTAINER_NAME:-radarr}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### radarr-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `radarr-nfs-media`, `radarr-nfs-downloads`
- **Adds/modifies services**: `radarr`

**Usage**:
```bash
make enable-override radarr-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/radarr-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable radarr

# Configure environment variables (if needed)
make scaffold radarr

# Start the service
make up
```
