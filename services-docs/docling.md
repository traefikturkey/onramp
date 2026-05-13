# Docling

> AI-powered document parsing and processing service with GPU acceleration

## Links
- [Official Repository](https://github.com/docling-project/docling-serve)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/docling.yml)

## Docker Images
- `ghcr.io/docling-project/docling-serve:${DOCLING_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCLING_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `DOCLING_CONTAINER_NAME` |  | Container name |
| `DOCLING_DOCKER_TAG` |  | Docker image tag/version |
| `DOCLING_ENABLE_UI` |  | Docling enable ui |
| `DOCLING_GPU_COUNT` |  | Docling gpu count |
| `DOCLING_NUM_THREADS` |  | Docling num threads |
| `DOCLING_PORT` |  | Service port number |
| `DOCLING_RESTART` |  | Container restart policy |
| `DOCLING_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `DOCLING_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${DOCLING_PORT:-5001}:5001`

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DOCLING_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.docling.entrypoints=websecure`
- `traefik.http.routers.docling.rule=Host(`${DOCLING_CONTAINER_NAME:-docling}.${HOST_DOMAIN}`)`
- `traefik.http.services.docling.loadbalancer.server.port=5001`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCLING_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${DOCLING_AUTOHEAL:-true}`
- `joyride.host.name=${DOCLING_CONTAINER_NAME:-docling}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable docling

# Configure environment variables (if needed)
make scaffold docling

# Start the service
make up
```
