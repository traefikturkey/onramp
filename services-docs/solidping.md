# SolidPing

> Uptime and synthetic monitoring with status pages, incidents and on-call alerts

## Links
- [Official Repository](https://github.com/fclairamb/solidping)
- [Official Documentation](https://docs.solidping.io)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/solidping.yml)

## Docker Images
- `ghcr.io/fclairamb/solidping:${SOLIDPING_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SOLIDPING_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `SOLIDPING_CONTAINER_NAME` |  | Container name |
| `SOLIDPING_DOCKER_TAG` |  | Docker image tag/version |
| `SOLIDPING_HOST_NAME` |  | Solidping host name |
| `SOLIDPING_RESTART` |  | Container restart policy |
| `SOLIDPING_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `SOLIDPING_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/solidping:/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=${SOLIDPING_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.solidping.entrypoints=websecure`
- `traefik.http.routers.solidping.middlewares=default-headers@file`
- `traefik.http.routers.solidping.rule=Host(`${SOLIDPING_HOST_NAME:-solidping}.${HOST_DOMAIN}`)`
- `traefik.http.routers.solidping.service=solidping`
- `traefik.http.routers.solidping.tls=true`
- `traefik.http.services.solidping.loadbalancer.server.port=4000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SOLIDPING_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${SOLIDPING_AUTOHEAL:-true}`
- `joyride.host.name=${SOLIDPING_HOST_NAME:-solidping}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable-service solidping

# Configure environment variables (if needed)
make edit-env solidping

# Start the service
make start-service solidping
```
