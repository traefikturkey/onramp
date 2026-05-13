# Fooocus

> Focus on prompting and generating | a generative image generator

## Links
- [Official Repository](https://github.com/lllyasviel/Fooocus/pkgs/container/fooocus)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/fooocus.yml)

## Docker Images
- `ghcr.io/lllyasviel/fooocus:${FOOOCUS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FOOOCUS_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `FOOOCUS_CONTAINER_NAME` |  | Container name |
| `FOOOCUS_DOCKER_TAG` |  | Docker image tag/version |
| `FOOOCUS_HOST_NAME` |  | Fooocus host name |
| `FOOOCUS_MEM_LIMIT` |  | Fooocus mem limit |
| `FOOOCUS_RESTART` |  | Container restart policy |
| `FOOOCUS_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `FOOOCUS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/fooocus:/content/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${FOOOCUS_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.fooocus.entrypoints=websecure`
- `traefik.http.routers.fooocus.rule=Host(`${FOOOCUS_HOST_NAME:-fooocus}.${HOST_DOMAIN}`)`
- `traefik.http.services.fooocus.loadbalancer.server.port=7865`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FOOOCUS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${FOOOCUS_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${FOOOCUS_HOST_NAME:-fooocus}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable fooocus

# Configure environment variables (if needed)
make scaffold fooocus

# Start the service
make up
```
