# Netbootxyz

> Network boot server for various operating systems

## Links
- [Official Repository](https://github.com/netbootxyz/docker-netbootxyz)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/netbootxyz.yml)

## Docker Images
- `ghcr.io/netbootxyz/netbootxyz:${NETBOOTXYZ_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NETBOOTXYZ_CONTAINER_NAME` |  | Container name |
| `NETBOOTXYZ_DOCKER_TAG` |  | Docker image tag/version |
| `NETBOOTXYZ_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `3000:3000`
- `69:69/udp`

### Volumes
- `./etc/netbootxyz:/config` - Volume mount
- `./media/netbootxyz:/assets` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.netbootxyz.entrypoints=websecure`
- `traefik.http.routers.netbootxyz.rule=Host(`${NETBOOTXYZ_CONTAINER_NAME:-netbootxyz}.${HOST_DOMAIN}`)`
- `traefik.http.services.netbootxyz.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NETBOOTXYZ_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${NETBOOTXYZ_CONTAINER_NAME:-netbootxyz}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable netbootxyz

# Configure environment variables (if needed)
make scaffold netbootxyz

# Start the service
make up
```
