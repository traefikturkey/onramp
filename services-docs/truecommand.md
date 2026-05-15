# Truecommand

> Management tool for truenas

## Links
- [Docker Image](https://hub.docker.com/r/ixsystems/truecommand)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/truecommand.yml)

## Docker Images
- `ghcr.io/ixsystems/truecommand:${TRUECOMMAND_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TRUECOMMAND_CONTAINER_NAME` |  | Container name |
| `TRUECOMMAND_DOCKER_TAG` |  | Docker image tag/version |
| `TRUECOMMAND_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/truecommand:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.truecommand.entrypoints=websecure`
- `traefik.http.routers.truecommand.rule=Host(`${TRUECOMMAND_CONTAINER_NAME:-truecommand}.${HOST_DOMAIN}`)`
- `traefik.http.services.truecommand.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TRUECOMMAND_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${TRUECOMMAND_CONTAINER_NAME:-truecommand}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable truecommand

# Configure environment variables (if needed)
make scaffold truecommand

# Start the service
make up
```
