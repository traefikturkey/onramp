# Streaming Search

> (Archived Project) Global Streaming Search Service

## Links
- [Official Repository](https://github.com/Colaski/global-streaming-search)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/streaming-search.yml)

## Docker Images
- `colaski/global-streaming-search:${STREAMING_SEARCH_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `STREAMING_SEARCH_CONTAINER_NAME` |  | Container name |
| `STREAMING_SEARCH_DOCKER_TAG` |  | Docker image tag/version |
| `STREAMING_SEARCH_RESTART` |  | Container restart policy |
| `STREAMING_SEARCH_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.streaming-search.entrypoints=websecure`
- `traefik.http.routers.streaming-search.rule=Host(`${STREAMING_SEARCH_CONTAINER_NAME:-streaming-search}.${HOST_DOMAIN}`)`
- `traefik.http.services.streaming-search.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${STREAMING_SEARCH_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${STREAMING_SEARCH_CONTAINER_NAME:-streaming-search}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable streaming-search

# Configure environment variables (if needed)
make scaffold streaming-search

# Start the service
make up
```
