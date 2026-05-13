# Paperless Ai

> An automated document analyzer for Paperless-ngx using OpenAI API

## Links
- [Official Repository](https://github.com/clusterzx/paperless-ai)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/paperless-ai.yml)

## Docker Images
- `clusterzx/paperless-ai:${PAPERLESS_AI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PAPERLESS_AI_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `PAPERLESS_AI_CONTAINER_NAME` |  | Container name |
| `PAPERLESS_AI_DOCKER_TAG` |  | Docker image tag/version |
| `PAPERLESS_AI_HOST_NAME` |  | Paperless ai host name |
| `PAPERLESS_AI_MEM_LIMIT` |  | Paperless ai mem limit |
| `PAPERLESS_AI_RESTART` |  | Container restart policy |
| `PAPERLESS_AI_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `PAPERLESS_AI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/paperless-ai:/app/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${PAPERLESS_AI_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.paperless-ai.entrypoints=websecure`
- `traefik.http.routers.paperless-ai.rule=Host(`${PAPERLESS_AI_HOST_NAME:-paperless-ai}.${HOST_DOMAIN}`)`
- `traefik.http.services.paperless-ai.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PAPERLESS_AI_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${PAPERLESS_AI_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${PAPERLESS_AI_HOST_NAME:-paperless-ai}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable paperless-ai

# Configure environment variables (if needed)
make scaffold paperless-ai

# Start the service
make up
```
