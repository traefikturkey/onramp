# Obsidian

> self hosted Notes app

## Links
- [Official Documentation](https://obsidian.md/community)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/obsidian.yml)

## Docker Images
- `lscr.io/linuxserver/obsidian:${OBSIDIAN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OBSIDIAN_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `OBSIDIAN_CONTAINER_NAME` |  | Container name |
| `OBSIDIAN_DOCKER_TAG` |  | Docker image tag/version |
| `OBSIDIAN_HOST_NAME` |  | Obsidian host name |
| `OBSIDIAN_RESTART` |  | Container restart policy |
| `OBSIDIAN_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `OBSIDIAN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/obsidian/config:/config` - Configuration files
- `./etc/obsidian/data:/data` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${OBSIDIAN_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.obsidian.entrypoints=websecure`
- `traefik.http.routers.obsidian.rule=Host(`${OBSIDIAN_HOST_NAME:-obsidian}.${HOST_DOMAIN}`)`
- `traefik.http.services.obsidian.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OBSIDIAN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${OBSIDIAN_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${OBSIDIAN_HOST_NAME:-obsidian}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### obsidian-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `obsidian-nfs-data`
- **Adds/modifies services**: `obsidian`

**Usage**:
```bash
make enable-override obsidian-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/obsidian-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable obsidian

# Configure environment variables (if needed)
make scaffold obsidian

# Start the service
make up
```
