# Qdirstat

> Disk space analyzer and cleanup tool

## Links
- [Official Repository](https://github.com/linuxserver/docker-qdirstat)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/qdirstat.yml)

## Docker Images
- `lscr.io/linuxserver/qdirstat:${QDIRSTAT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `QDIRSTAT_CONTAINER_NAME` |  | Container name |
| `QDIRSTAT_DOCKER_TAG` |  | Docker image tag/version |
| `QDIRSTAT_MEDIA_VOLUME` |  | Qdirstat media volume |
| `QDIRSTAT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/qdirstat:/config` - Volume mount
- `./etc/qdirstat/nginx-default.conf:/etc/nginx/sites-enabled/default` - Volume mount
- `${QDIRSTAT_MEDIA_VOLUME:-./media}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.qdirstat.entrypoints=websecure`
- `traefik.http.routers.qdirstat.rule=Host(`${QDIRSTAT_CONTAINER_NAME:-qdirstat}.${HOST_DOMAIN}`)`
- `traefik.http.services.qdirstat.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${QDIRSTAT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${QDIRSTAT_CONTAINER_NAME:-qdirstat}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### qdirstat-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `qdirstat-nfs-volume`
- **Adds/modifies services**: `qdirstat`

**Usage**:
```bash
make enable-override qdirstat-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/qdirstat-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable qdirstat

# Configure environment variables (if needed)
make scaffold qdirstat

# Start the service
make up
```
