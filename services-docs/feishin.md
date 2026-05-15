# Feishin

> A modern self-hosted music player.

## Links
- [Official Repository](https://github.com/jeffvli/feishin)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/feishin.yml)

## Docker Images
- `ghcr.io/jeffvli/feishin:${FEISHIN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FEISHIN_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `FEISHIN_CONTAINER_NAME` |  | Container name |
| `FEISHIN_DOCKER_TAG` |  | Docker image tag/version |
| `FEISHIN_HOST_NAME` |  | Feishin host name |
| `FEISHIN_MEM_LIMIT` |  | Feishin mem limit |
| `FEISHIN_RESTART` |  | Container restart policy |
| `FEISHIN_SERVER_LOCK` |  | Feishin server lock |
| `FEISHIN_SERVER_NAME` |  | Feishin server name |
| `FEISHIN_SERVER_TYPE` |  | Feishin server type |
| `FEISHIN_SERVER_URL` |  | Feishin server url |
| `FEISHIN_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `FEISHIN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
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
- `traefik.enable=${FEISHIN_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.feishin.entrypoints=websecure`
- `traefik.http.routers.feishin.middlewares=default-headers@file`
- `traefik.http.routers.feishin.rule=Host(`${FEISHIN_HOST_NAME:-feishin}.${HOST_DOMAIN}`)`
- `traefik.http.services.feishin.loadbalancer.server.port=9180`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FEISHIN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${FEISHIN_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${FEISHIN_HOST_NAME:-feishin}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable feishin

# Configure environment variables (if needed)
make scaffold feishin

# Start the service
make up
```
