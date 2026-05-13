# Firefly Data Importer

> Imports data into firefly iii, a personal finance manager

## Links
- [Official Repository](https://github.com/firefly-iii/firefly-iii/tree/main)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/firefly-data-importer.yml)

## Docker Images
- `fireflyiii/data-importer:${FIREFLY_DATA_IMPORTER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FIREFLY3_CONTAINER_NAME` |  | Container name |
| `FIREFLY_DATA_IMPORTER_CONTAINER_NAME` |  | Container name |
| `FIREFLY_DATA_IMPORTER_DOCKER_TAG` |  | Docker image tag/version |
| `FIREFLY_DATA_IMPORTER_RESTART` |  | Container restart policy |
| `FIREFLY_DATA_IMPORTER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `FIREFLY_III_ACCESS_TOKEN_JWT` |  | Firefly iii access token jwt |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `81:8080`

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.firefly-data-importer.entrypoints=websecure`
- `traefik.http.routers.firefly-data-importer.rule=Host(`${FIREFLY_DATA_IMPORTER_CONTAINER_NAME:-firefly-importer}.${HOST_DOMAIN}`)`
- `traefik.http.services.firefly-data-importer.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FIREFLY_DATA_IMPORTER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FIREFLY_DATA_IMPORTER_CONTAINER_NAME:-firefly-importer}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable firefly-data-importer

# Configure environment variables (if needed)
make scaffold firefly-data-importer

# Start the service
make up
```
