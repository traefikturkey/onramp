# Owncast

> Self-hosted live video streaming server

## Links
- [Official Repository](https://github.com/owncast/owncast)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/owncast.yml)

## Docker Images
- `owncast/owncast:${OWNCAST_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OWNCAST_CONTAINER_NAME` |  | Container name |
| `OWNCAST_DOCKER_TAG` |  | Docker image tag/version |
| `OWNCAST_RESTART` |  | Container restart policy |
| `OWNCAST_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `1935:1935`

### Volumes
- `./etc/owncast:/app/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.owncast.entrypoints=websecure`
- `traefik.http.routers.owncast.rule=Host(`${OWNCAST_CONTAINER_NAME:-owncast}.${HOST_DOMAIN}`)`
- `traefik.http.services.owncast.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OWNCAST_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${OWNCAST_CONTAINER_NAME:-owncast}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### owncast-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `owncast-nfs-data`
- **Adds/modifies services**: `owncast`

**Usage**:
```bash
make enable-override owncast-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/owncast-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable owncast

# Configure environment variables (if needed)
make scaffold owncast

# Start the service
make up
```
