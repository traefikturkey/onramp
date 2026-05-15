# Bind

> A very flexible, full-featured DNS system

## Links
- [Docker Image](https://hub.docker.com/r/ubuntu/bind9)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/bind.yml)

## Docker Images
- `ubuntu/bind9:${BIND_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BIND_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `BIND_CONTAINER_NAME` |  | Container name |
| `BIND_DOCKER_TAG` |  | Docker image tag/version |
| `BIND_MEM_LIMIT` |  | Bind mem limit |
| `BIND_PORT` |  | Service port number |
| `BIND_RESTART` |  | Container restart policy |
| `BIND_USER` |  | Service username |
| `BIND_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${BIND_PORT:-53}:53/tcp`
- `${BIND_PORT:-53}:53/udp`

### Volumes
- `./etc/bind/config:/etc/bind` - Configuration files
- `./etc/bind/cache:/var/cache/bind` - Volume mount
- `./etc/bind/records:/var/lib/bind` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BIND_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${BIND_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable bind

# Configure environment variables (if needed)
make scaffold bind

# Start the service
make up
```
