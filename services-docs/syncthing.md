# Syncthing

> Decentralized file synchronization tool

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/syncthing)
- [Official Documentation](https://docs.linuxserver.io/images/docker-syncthing)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/syncthing.yml)

## Docker Images
- `lscr.io/linuxserver/syncthing:${SYNCTHING_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SYNCTHING_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `SYNCTHING_CONTAINER_NAME` |  | Container name |
| `SYNCTHING_DOCKER_TAG` |  | Docker image tag/version |
| `SYNCTHING_MEM_LIMIT` |  | Syncthing mem limit |
| `SYNCTHING_RESTART` |  | Container restart policy |
| `SYNCTHING_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `SYNCTHING_VOLUME` |  | Syncthing volume |
| `SYNCTHING_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `22000:22000`
- `21027:21027/udp`

### Volumes
- `./etc/syncthing:/config` - Volume mount
- `${SYNCTHING_VOLUME:-./media/sync}` - Volume mount
- `/dev/rtc:/dev/rtc` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SYNCTHING_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.sync.entrypoints=websecure`
- `traefik.http.routers.sync.rule=Host(`${SYNCTHING_CONTAINER_NAME:-syncthing}.${HOST_DOMAIN}`)`
- `traefik.http.services.sync.loadbalancer.server.port=8384`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SYNCTHING_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${SYNCTHING_AUTOHEAL:-true}`
- `joyride.host.name=${SYNCTHING_CONTAINER_NAME:-syncthing}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### syncthing-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `syncthing-nfs-media`
- **Adds/modifies services**: `syncthing`

**Usage**:
```bash
make enable-override syncthing-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/syncthing-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable syncthing

# Configure environment variables (if needed)
make scaffold syncthing

# Start the service
make up
```
