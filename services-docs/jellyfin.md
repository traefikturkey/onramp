# Jellyfin

> Media server for streaming content

## Links
- [Official Repository](https://github.com/linuxserver/docker-jellyfin)
- [Docker Image](https://hub.docker.com/r/linuxserver/jellyfin)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/jellyfin.yml)

## Docker Images
- `lscr.io/linuxserver/jellyfin:${JELLYFIN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `JELLYFIN_CONFIG_PATH` |  | Jellyfin config path |
| `JELLYFIN_CONTAINER_NAME` |  | Container name |
| `JELLYFIN_DOCKER_TAG` |  | Docker image tag/version |
| `JELLYFIN_MEDIA_PATH` |  | Jellyfin media path |
| `JELLYFIN_MEDIA_VOLUME` |  | Jellyfin media volume |
| `JELLYFIN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `7359:7359/udp`

### Volumes
- `./etc/jellyfin:${JELLYFIN_CONFIG_PATH` - Volume mount
- `${JELLYFIN_MEDIA_VOLUME:-./media}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.jellyfin.entrypoints=websecure`
- `traefik.http.routers.jellyfin.rule=Host(`${JELLYFIN_CONTAINER_NAME:-jellyfin}.${HOST_DOMAIN}`)`
- `traefik.http.services.jellyfin.loadbalancer.server.port=8096`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${JELLYFIN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${JELLYFIN_CONTAINER_NAME:-jellyfin}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### jellyfin-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `jellyfin-nfs-media`
- **Adds/modifies services**: `jellyfin`

**Usage**:
```bash
make enable-override jellyfin-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/jellyfin-nfs.yml)

### jellyfin-nvidia

**Purpose**: Enables NVIDIA GPU hardware acceleration

**Changes**:
- **Adds/modifies services**: `jellyfin`
- **Adds/modifies environment variables**: `PUID`, `PGID`, `TZ`, `JELLYFIN_PublishedServerUrl`, `NVIDIA_DRIVER_CAPABILITIES`, `NVIDIA_VISIBLE_DEVICES`

**Usage**:
```bash
make enable-override jellyfin-nvidia
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/jellyfin-nvidia.yml)

### jellyfin-quicksync

**Purpose**: Enables Intel QuickSync hardware acceleration

**Changes**:
- **Adds/modifies services**: `jellyfin`

**Usage**:
```bash
make enable-override jellyfin-quicksync
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/jellyfin-quicksync.yml)

## Quick Start

```bash
# Enable the service
make enable jellyfin

# Configure environment variables (if needed)
make scaffold jellyfin

# Start the service
make up
```
