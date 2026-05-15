# Audiobookshelf

> Manages and serves audiobooks

## Links
- [Official Repository](https://github.com/advplyr/audiobookshelf)
- [Docker Image](https://hub.docker.com/r/advplyr/audiobookshelf)
- [Official Documentation](https://www.audiobookshelf.org/docs/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/audiobookshelf.yml)

## Docker Images
- `ghcr.io/advplyr/audiobookshelf:${AUDIOBOOKSHELF_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIOBOOKSHELF_CONTAINER_NAME` |  | Container name |
| `AUDIOBOOKSHELF_DOCKER_TAG` |  | Docker image tag/version |
| `AUDIOBOOKSHELF_MEDIA_AUDIOBOOKS` |  | Audiobookshelf media audiobooks |
| `AUDIOBOOKSHELF_MEDIA_AUDIOBOOKS_PATH` |  | Audiobookshelf media audiobooks path |
| `AUDIOBOOKSHELF_MEDIA_PODCASTS` |  | Audiobookshelf media podcasts |
| `AUDIOBOOKSHELF_MEDIA_PODCASTS_PATH` |  | Audiobookshelf media podcasts path |
| `AUDIOBOOKSHELF_RESTART` |  | Container restart policy |
| `AUDIOBOOKSHELF_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/audiobookshelf/config:/config` - Configuration files
- `./etc/audiobookshelf/metadata:/metadata` - Data storage
- `${AUDIOBOOKSHELF_MEDIA_AUDIOBOOKS:-./media/audiobooks}` - Volume mount
- `${AUDIOBOOKSHELF_MEDIA_PODCASTS:-./media/podcasts}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.audiobookshelf.entrypoints=websecure`
- `traefik.http.routers.audiobookshelf.rule=Host(`${AUDIOBOOKSHELF_CONTAINER_NAME:-audiobookshelf}.${HOST_DOMAIN}`)`
- `traefik.http.services.audiobookshelf.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${AUDIOBOOKSHELF_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${AUDIOBOOKSHELF_CONTAINER_NAME:-audiobookshelf}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### audiobookshelf-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `audiobookshelf-nfs-media`, `audiobookshelf-nfs-podcasts`
- **Adds/modifies services**: `audiobookshelf`

**Usage**:
```bash
make enable-override audiobookshelf-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/audiobookshelf-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable audiobookshelf

# Configure environment variables (if needed)
make scaffold audiobookshelf

# Start the service
make up
```
