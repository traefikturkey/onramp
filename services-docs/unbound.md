# Unbound

> Dns resolver

## Links
- [Official Repository](https://github.com/pascaliske/docker-unbound)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/unbound.yml)

## Docker Images
- `ghcr.io/pascaliske/unbound:${UNBOUND_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `UNBOUND_CONTAINER_NAME` |  | Container name |
| `UNBOUND_DOCKER_TAG` |  | Docker image tag/version |
| `UNBOUND_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${UNBOUND_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable unbound

# Configure environment variables (if needed)
make scaffold unbound

# Start the service
make up
```
