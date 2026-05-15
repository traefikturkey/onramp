# Searxng

> Self-hosted metasearch engine

## Links
- [Official Repository](https://github.com/searxng/searxng-docker)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/searxng.yml)

## Docker Images
- `ghcr.io/searxng/searxng:${SEARXNG_DOCKER_TAG:-latest}`
- `redis:alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SEARXNG_CONTAINER_NAME` |  | Container name |
| `SEARXNG_DOCKER_TAG` |  | Docker image tag/version |
| `SEARXNG_HOSTNAME` |  | Searxng hostname |
| `SEARXNG_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${SEARXNG_VOLUME-./etc/searxng}:/etc/searxng` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.searxng.entrypoints=websecure`
- `traefik.http.routers.searxng.rule=Host(`${SEARXNG_CONTAINER_NAME:-searxng}.${HOST_DOMAIN}`)`
- `traefik.http.services.searxng.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SEARXNG_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SEARXNG_CONTAINER_NAME:-searxng}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable searxng

# Configure environment variables (if needed)
make scaffold searxng

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
