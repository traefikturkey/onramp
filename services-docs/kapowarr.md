# Kapowarr

> Manages comic book collections and downloads

## Links
- [Official Repository](https://github.com/Casvt/Kapowarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/kapowarr.yml)

## Docker Images
- `mrcas/kapowarr:${KAPOWARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KAPOWARR_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `KAPOWARR_CONTAINER_NAME` |  | Container name |
| `KAPOWARR_DOCKER_TAG` |  | Docker image tag/version |
| `KAPOWARR_RESTART` |  | Container restart policy |
| `KAPOWARR_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `KAPOWARR_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `MEDIA_COMICS_VOLUME` |  | Media comics volume |
| `MEDIA_DOWNLOADS_VOLUME` |  | Media downloads volume |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/kapowarr/db:/app/db` - Volume mount
- `${MEDIA_COMICS_VOLUME:-./media/comics}` - Volume mount
- `${MEDIA_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount
- `/dev/rtc:/dev/rtc` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${KAPOWARR_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.kapowarr.entrypoints=websecure`
- `traefik.http.routers.kapowarr.rule=Host(`${KAPOWARR_CONTAINER_NAME:-kapowarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.kapowarr.loadbalancer.server.port=5656`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KAPOWARR_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${KAPOWARR_AUTOHEAL:-true}`
- `joyride.host.name=${KAPOWARR_CONTAINER_NAME:-kapowarr}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### kapowarr-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `kapowarr-nfs-media`, `kapowarr-nfs-downloads`
- **Adds/modifies services**: `kapowarr`

**Usage**:
```bash
make enable-override kapowarr-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/kapowarr-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable kapowarr

# Configure environment variables (if needed)
make scaffold kapowarr

# Start the service
make up
```
