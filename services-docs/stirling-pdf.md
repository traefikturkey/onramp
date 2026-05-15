# Stirling Pdf

> Container for running stirling pdf, a web-based pdf viewer

## Links
- [Official Repository](https://github.com/Stirling-Tools/Stirling-PDF)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/stirling-pdf.yml)

## Docker Images
- `ghcr.io/stirling-tools/stirling-pdf:${STIRLING_PDF_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `STIRLING_PDF_CONTAINER_NAME` |  | Container name |
| `STIRLING_PDF_DOCKER_TAG` |  | Docker image tag/version |
| `STIRLING_PDF_FLAME_ICON` |  | Stirling pdf flame icon |
| `STIRLING_PDF_FLAME_NAME` |  | Stirling pdf flame name |
| `STIRLING_PDF_LOCALE` |  | Stirling pdf locale |
| `STIRLING_PDF_RESTART` |  | Container restart policy |
| `STIRLING_PDF_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/stirling-pdf/configs:/configs` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.middlewares.limit.buffering.maxRequestBodyBytes=10000000000`
- `traefik.http.routers.stirling-pdf.entrypoints=websecure`
- `traefik.http.routers.stirling-pdf.middlewares=limit`
- `traefik.http.routers.stirling-pdf.rule=Host(`${STIRLING_PDF_CONTAINER_NAME:-stirling-pdf}.${HOST_DOMAIN}`)`
- `traefik.http.services.stirling-pdf.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${STIRLING_PDF_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `flame.icon=${STIRLING_PDF_FLAME_ICON:-docker}`
- `flame.name=${STIRLING_PDF_FLAME_NAME:-stirling-pdf}`
- `flame.type=application`
- `flame.url=https://${STIRLING_PDF_CONTAINER_NAME:-stirling-pdf}.${HOST_DOMAIN}`
- `joyride.host.name=${STIRLING_PDF_CONTAINER_NAME:-stirling-pdf}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable stirling-pdf

# Configure environment variables (if needed)
make scaffold stirling-pdf

# Start the service
make up
```
