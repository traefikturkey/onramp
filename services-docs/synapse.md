# Synapse

> Matrix communication server

## Links
- [Official Repository](https://github.com/matrix-org/synapse)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/synapse.yml)

## Docker Images
- `ghcr.io/matrix-org/synapse:${SYNAPSE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SYNAPSE_CONTAINER_NAME` |  | Container name |
| `SYNAPSE_DOCKER_TAG` |  | Docker image tag/version |
| `SYNAPSE_RESTART` |  | Container restart policy |
| `SYNAPSE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/synapse:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.synapse.entrypoints=websecure`
- `traefik.http.routers.synapse.rule=Host(`${SYNAPSE_CONTAINER_NAME:-synapse}.${HOST_DOMAIN}`)`
- `traefik.http.services.synapse.loadbalancer.server.port=8008`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SYNAPSE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SYNAPSE_CONTAINER_NAME:-synapse}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable synapse

# Configure environment variables (if needed)
make scaffold synapse

# Start the service
make up
```
