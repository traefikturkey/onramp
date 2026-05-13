# Unmanic

> Unmanic is a simple tool for optimising your file library

## Links
- [Official Repository](https://github.com/Unmanic/unmanic)
- [Official Documentation](https://docs.unmanic.app/docs/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/unmanic.yml)

## Docker Images
- `josh5/unmanic:${UNMANIC_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `UNMANIC_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `UNMANIC_CONTAINER_NAME` |  | Container name |
| `UNMANIC_DOCKER_TAG` |  | Docker image tag/version |
| `UNMANIC_HOST_NAME` |  | Unmanic host name |
| `UNMANIC_MEM_LIMIT` |  | Unmanic mem limit |
| `UNMANIC_RESTART` |  | Container restart policy |
| `UNMANIC_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `UNMANIC_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/unmanic:/config` - Volume mount
- `./media:/library` - Volume mount
- `./etc/unmanic/cache:/tmp/unmanic` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${UNMANIC_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.unmanic.entrypoints=websecure`
- `traefik.http.routers.unmanic.rule=Host(`${UNMANIC_HOST_NAME:-unmanic}.${HOST_DOMAIN}`)`
- `traefik.http.services.unmanic.loadbalancer.server.port=8888`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${UNMANIC_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${UNMANIC_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${UNMANIC_HOST_NAME:-unmanic}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable unmanic

# Configure environment variables (if needed)
make scaffold unmanic

# Start the service
make up
```
