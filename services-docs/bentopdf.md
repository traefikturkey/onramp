# Bentopdf

> Privacy-first, client-side PDF toolkit for editing, merging, and processing PDFs in the browser

## Links
- [Official Repository](https://github.com/alam00000/bentopdf)
- [Docker Image](https://hub.docker.com/r/bentopdf/bentopdf-simple)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/bentopdf.yml)

## Docker Images
- `bentopdf/bentopdf-simple:${BENTOPDF_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BENTOPDF_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `BENTOPDF_CONTAINER_NAME` |  | Container name |
| `BENTOPDF_DOCKER_TAG` |  | Docker image tag/version |
| `BENTOPDF_HOST_NAME` |  | Bentopdf host name |
| `BENTOPDF_RESTART` |  | Container restart policy |
| `BENTOPDF_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `BENTOPDF_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${BENTOPDF_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.bentopdf.entrypoints=websecure`
- `traefik.http.routers.bentopdf.rule=Host(`${BENTOPDF_HOST_NAME:-bentopdf}.${HOST_DOMAIN}`)`
- `traefik.http.services.bentopdf.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BENTOPDF_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${BENTOPDF_AUTOHEAL:-true}`
- `joyride.host.name=${BENTOPDF_HOST_NAME:-bentopdf}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable bentopdf

# Configure environment variables (if needed)
make scaffold bentopdf

# Start the service
make up
```
