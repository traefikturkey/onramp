# Homepage

> Customizable start page for web browsers

## Links
- [Official Repository](https://github.com/gethomepage/homepage//wiki/Service-Discovery)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/homepage.yml)

## Docker Images
- `ghcr.io/gethomepage/homepage:${HOMEPAGE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOMEPAGE_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `HOMEPAGE_CONTAINER_NAME` |  | Container name |
| `HOMEPAGE_DOCKER_TAG` |  | Docker image tag/version |
| `HOMEPAGE_MEM_LIMIT` |  | Homepage mem limit |
| `HOMEPAGE_RESTART` |  | Container restart policy |
| `HOMEPAGE_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `HOMEPAGE_WATCHTOWER` |  | Homepage watchtower |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/homepage:/app/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${HOMEPAGE_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.homepage.entrypoints=websecure`
- `traefik.http.routers.homepage.rule=Host(`${HOMEPAGE_CONTAINER_NAME:-homepage}.${HOST_DOMAIN}`)`
- `traefik.http.services.homepage.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HOMEPAGE_WATCHTOWER:-true}`

**Other Labels:**
- `autoheal=${HOMEPAGE_AUTOHEAL:-true}`
- `joyride.host.name=${HOMEPAGE_CONTAINER_NAME:-homepage}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable homepage

# Configure environment variables (if needed)
make scaffold homepage

# Start the service
make up
```
