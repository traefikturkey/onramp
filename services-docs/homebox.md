# Homebox

> Inventory and organization system for your home

## Links
- [Official Repository](https://github.com/sysadminsmedia/homebox)
- [Official Documentation](https://homebox.software/en/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/homebox.yml)

## Docker Images
- `ghcr.io/sysadminsmedia/homebox:${HOMEBOX_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOMEBOX_CONTAINER_NAME` |  | Container name |
| `HOMEBOX_DOCKER_TAG` |  | Docker image tag/version |
| `HOMEBOX_RESTART` |  | Container restart policy |
| `HOMEBOX_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/homebox:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.homebox.entrypoints=websecure`
- `traefik.http.routers.homebox.rule=Host(`${HOMEBOX_CONTAINER_NAME:-homebox}.${HOST_DOMAIN}`)`
- `traefik.http.services.homebox.loadbalancer.server.port=7745`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HOMEBOX_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${HOMEBOX_CONTAINER_NAME:-homebox}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### homebox-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `homebox-nfs-data`
- **Adds/modifies services**: `homebox`

**Usage**:
```bash
make enable-override homebox-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/homebox-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable homebox

# Configure environment variables (if needed)
make scaffold homebox

# Start the service
make up
```
