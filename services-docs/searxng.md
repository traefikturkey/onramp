# Searxng

> Self-hosted metasearch engine

## Links
- [Official Documentation](https://docs.searxng.org/admin/installation-docker.html)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/searxng.yml)

## Docker Images
- `ghcr.io/searxng/searxng:${SEARXNG_DOCKER_TAG:-latest}`
- `valkey/valkey:${SEARXNG_VALKEY_DOCKER_TAG:-9-alpine}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `SEARXNG_AUTOHEAL` | false | Enable Autoheal container restart on unhealthy status |
| `SEARXNG_CACHE_VOLUME` | ./media/searxng/cache | Searxng cache volume |
| `SEARXNG_CONTAINER_NAME` | searxng | Container name |
| `SEARXNG_DOCKER_TAG` | latest | Docker image tag/version |
| `SEARXNG_HOST_NAME` | searxng | Searxng host name |
| `SEARXNG_RESTART` | unless-stopped | Container restart policy |
| `SEARXNG_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `SEARXNG_VALKEY_AUTOHEAL` | false | Enable Autoheal container restart on unhealthy status |
| `SEARXNG_VALKEY_CONTAINER_NAME` | searxng-valkey | Container name |
| `SEARXNG_VALKEY_DOCKER_TAG` | 9-alpine | Docker image tag/version |
| `SEARXNG_VALKEY_RESTART` | unless-stopped | Container restart policy |
| `SEARXNG_VALKEY_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `SEARXNG_VOLUME` | ./etc/searxng | Searxng volume |
| `SEARXNG_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${SEARXNG_VOLUME:-./etc/searxng}` - Volume mount
- `${SEARXNG_CACHE_VOLUME:-./media/searxng/cache}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./media/searxng/valkey:/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`
- `traefik.http.routers.searxng.entrypoints=websecure`
- `traefik.http.routers.searxng.rule=Host(`${SEARXNG_HOST_NAME:-searxng}.${HOST_DOMAIN}`)`
- `traefik.http.services.searxng.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SEARXNG_VALKEY_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${SEARXNG_VALKEY_AUTOHEAL:-false}`
- `joyride.host.name=${SEARXNG_HOST_NAME:-searxng}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `searxng-valkey`

## Quick Start

```bash
# Enable the service
make enable-service searxng

# Configure environment variables (if needed)
make edit-env searxng

# Start the service
make start-service searxng
```

## Notes
- This service consists of 2 containers working together
- Requires searxng-valkey to be running
