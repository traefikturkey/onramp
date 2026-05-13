# Mealie

> Recipe management system

## Links
- [Official Repository](https://github.com/mealie-recipes/mealie)
- [Docker Image](https://hub.docker.com/r/hkotel/mealie)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mealie.yml)

## Docker Images
- `ghcr.io/mealie-recipes/mealie:${MEALIE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MEALIE_CONTAINER_NAME` |  | Container name |
| `MEALIE_DOCKER_TAG` |  | Docker image tag/version |
| `MEALIE_RESTART` |  | Container restart policy |
| `MEALIE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/mealie:/app/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.mealie.entrypoints=websecure`
- `traefik.http.routers.mealie.rule=Host(`${MEALIE_CONTAINER_NAME:-mealie}.${HOST_DOMAIN}`)`
- `traefik.http.services.mealie.loadbalancer.server.port=9000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MEALIE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MEALIE_CONTAINER_NAME:-mealie}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### mealie-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `mealie-nfs-data`
- **Adds/modifies services**: `mealie`

**Usage**:
```bash
make enable-override mealie-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/mealie-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable mealie

# Configure environment variables (if needed)
make scaffold mealie

# Start the service
make up
```
