# Copyparty

> Portable file server with accelerated resumable uploads, dedup, WebDAV, FTP, TFTP, zeroconf, media indexer, thumbnails

## Links
- [Official Repository](https://github.com/9001/copyparty)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/copyparty.yml)

## Docker Images
- `copyparty/ac:${COPYPARTY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COPYPARTY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `COPYPARTY_CONTAINER_NAME` |  | Container name |
| `COPYPARTY_DOCKER_TAG` |  | Docker image tag/version |
| `COPYPARTY_HOST_NAME` |  | Copyparty host name |
| `COPYPARTY_MEM_LIMIT` |  | Copyparty mem limit |
| `COPYPARTY_RESTART` |  | Container restart policy |
| `COPYPARTY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `COPYPARTY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/copyparty/config:/cfg` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${COPYPARTY_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.copyparty.entrypoints=websecure`
- `traefik.http.routers.copyparty.rule=Host(`${COPYPARTY_HOST_NAME:-copyparty}.${HOST_DOMAIN}`)`
- `traefik.http.services.copyparty.loadbalancer.server.port=3923`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${COPYPARTY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${COPYPARTY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${COPYPARTY_HOST_NAME:-copyparty}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### copyparty-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `copyparty-nfs-media`
- **Adds/modifies services**: `copyparty`

**Usage**:
```bash
make enable-override copyparty-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/copyparty-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable copyparty

# Configure environment variables (if needed)
make scaffold copyparty

# Start the service
make up
```
