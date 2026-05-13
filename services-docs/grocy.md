# Grocy

> Web-based docker container grocery/household mgmt app

## Links
- [Official Repository](https://github.com/grocy/grocy)
- [Docker Image](https://hub.docker.com/r/linuxserver/grocy)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/grocy.yml)

## Docker Images
- `lscr.io/linuxserver/grocy:${GROCY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GROCY_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `GROCY_CONTAINER_NAME` |  | Container name |
| `GROCY_DOCKER_TAG` |  | Docker image tag/version |
| `GROCY_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `GROCY_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/grocy/config:/config` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${GROCY_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.grocy.entrypoints=websecure`
- `traefik.http.routers.grocy.rule=Host(`${GROCY_CONTAINER_NAME:-grocy}.${HOST_DOMAIN}`)`
- `traefik.http.services.grocy.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GROCY_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${GROCY_AUTOHEAL:-true}`
- `joyride.host.name=${GROCY_CONTAINER_NAME:-grocy}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable grocy

# Configure environment variables (if needed)
make scaffold grocy

# Start the service
make up
```
