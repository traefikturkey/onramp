# Lychee

> Photo management and sharing platform

## Links
- [Official Repository](https://github.com/LycheeOrg/Lychee-Docker)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/lychee.yml)

## Docker Images
- `lscr.io/linuxserver/lychee:${LYCHEE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `LYCHEE_DOCKER_TAG` |  | Docker image tag/version |
| `LYCHEE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/lychee:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.lychee.entrypoints=websecure`
- `traefik.http.routers.lychee.rule=Host(`lychee.${HOST_DOMAIN}`)`
- `traefik.http.services.lychee.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LYCHEE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=lychee.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### lychee-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `lychee-nfs-media`
- **Adds/modifies services**: `lychee`

**Usage**:
```bash
make enable-override lychee-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/lychee-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable lychee

# Configure environment variables (if needed)
make scaffold lychee

# Start the service
make up
```
