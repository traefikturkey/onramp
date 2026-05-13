# Prowlarr

> Container for running prowlarr, a media indexer

## Links
- [Official Repository](https://github.com/linuxserver/docker-prowlarr)
- [Docker Image](https://hub.docker.com/r/linuxserver/prowlarr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prowlarr.yml)

## Docker Images
- `lscr.io/linuxserver/prowlarr:${PROWLARR_DOCKER_TAG:-develop}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PROWLARR_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `PROWLARR_CONTAINER_NAME` |  | Container name |
| `PROWLARR_DOCKER_TAG` |  | Docker image tag/version |
| `PROWLARR_RESTART` |  | Container restart policy |
| `PROWLARR_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `PROWLARR_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `9696:9696`

### Volumes
- `./etc/prowlarr:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${PROWLARR_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.prowlarr.entrypoints=websecure`
- `traefik.http.routers.prowlarr.rule=Host(`${PROWLARR_CONTAINER_NAME:-prowlarr}.${HOST_DOMAIN}`)`
- `traefik.http.services.prowlarr.loadbalancer.server.port=9696`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PROWLARR_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${PROWLARR_AUTOHEAL:-true}`
- `joyride.host.name=${PROWLARR_CONTAINER_NAME:-prowlarr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable prowlarr

# Configure environment variables (if needed)
make scaffold prowlarr

# Start the service
make up
```
