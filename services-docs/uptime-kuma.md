# Uptime Kuma

> Self-hosted uptime monitoring tool

## Links
- [Official Repository](https://github.com/louislam/uptime-kuma)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/uptime-kuma.yml)

## Docker Images
- `louislam/uptime-kuma:${UPTIMEKUMA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |
| `UPTIMEKUMA_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `UPTIMEKUMA_CONTAINER_NAME` |  | Container name |
| `UPTIMEKUMA_DOCKER_SOCKET` |  | Uptimekuma docker socket |
| `UPTIMEKUMA_DOCKER_TAG` |  | Docker image tag/version |
| `UPTIMEKUMA_HOST_NAME` |  | Uptimekuma host name |
| `UPTIMEKUMA_MEM_LIMIT` |  | Uptimekuma mem limit |
| `UPTIMEKUMA_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `UPTIMEKUMA_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/uptime-kuma:/app/data` - Volume mount
- `${UPTIMEKUMA_DOCKER_SOCKET:-/var/run/docker.sock}` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=${UPTIMEKUMA_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.uptimekuma.entrypoints=websecure`
- `traefik.http.routers.uptimekuma.middlewares=default-headers@file`
- `traefik.http.routers.uptimekuma.rule=Host(`${UPTIMEKUMA_HOST_NAME:-uptimekuma}.${HOST_DOMAIN}`)`
- `traefik.http.routers.uptimekuma.service=uptimekuma`
- `traefik.http.routers.uptimekuma.tls=true`
- `traefik.http.services.uptimekuma.loadbalancer.server.port=3001`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${UPTIMEKUMA_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${UPTIMEKUMA_AUTOHEAL:-true}`
- `joyride.host.name=${UPTIMEKUMA_HOST_NAME:-uptimekuma}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable uptime-kuma

# Configure environment variables (if needed)
make scaffold uptime-kuma

# Start the service
make up
```
