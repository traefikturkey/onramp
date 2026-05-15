# Cup

> The easiest way to manage your container updates.

## Links
- [Official Repository](https://github.com/sergi0g/cup)
- [Official Documentation](https://cup.sergi0g.dev/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cup.yml)

## Docker Images
- `ghcr.io/sergi0g/cup:${CUP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CUP_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `CUP_CONTAINER_NAME` |  | Container name |
| `CUP_DOCKER_TAG` |  | Docker image tag/version |
| `CUP_HOST_NAME` |  | Cup host name |
| `CUP_MEM_LIMIT` |  | Cup mem limit |
| `CUP_RESTART` |  | Container restart policy |
| `CUP_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `CUP_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/cup:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CUP_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.cup.entrypoints=websecure`
- `traefik.http.routers.cup.rule=Host(`${CUP_HOST_NAME:-cup}.${HOST_DOMAIN}`)`
- `traefik.http.services.cup.loadbalancer.server.port=9000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CUP_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${CUP_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${CUP_HOST_NAME:-cup}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable cup

# Configure environment variables (if needed)
make scaffold cup

# Start the service
make up
```
