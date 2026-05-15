# Glance

> A self-hosted dashboard that puts all your feeds in one place

## Links
- [Official Repository](https://github.com/glanceapp/glance)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/glance.yml)

## Docker Images
- `glanceapp/glance:${GLANCE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GLANCE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `GLANCE_CONTAINER_NAME` |  | Container name |
| `GLANCE_DOCKER_TAG` |  | Docker image tag/version |
| `GLANCE_HOST_NAME` |  | Glance host name |
| `GLANCE_MEM_LIMIT` |  | Glance mem limit |
| `GLANCE_RESTART` |  | Container restart policy |
| `GLANCE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `GLANCE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/glance/:/app/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${GLANCE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.glance.entrypoints=websecure`
- `traefik.http.routers.glance.rule=Host(`${GLANCE_HOST_NAME:-glance}.${HOST_DOMAIN}`)`
- `traefik.http.services.glance.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GLANCE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${GLANCE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${GLANCE_HOST_NAME:-glance}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable glance

# Configure environment variables (if needed)
make scaffold glance

# Start the service
make up
```
