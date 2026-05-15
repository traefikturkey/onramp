# Nutify

> UPS Monitoring System

## Links
- [Official Repository](https://github.com/DartSteven/Nutify)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nutify.yml)

## Docker Images
- `dartsteven/nutify:${NUTIFY_DOCKER_TAG:-amd64-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NUTIFY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `NUTIFY_CONTAINER_NAME` |  | Container name |
| `NUTIFY_DOCKER_TAG` |  | Docker image tag/version |
| `NUTIFY_ENABLE_LOG_STARTUP` |  | Nutify enable log startup |
| `NUTIFY_ENCRYPTION_KEY` | CHANGE_ME_COPY_FROM_etc_nutify_keys_encryption-key_txt | Nutify encryption key |
| `NUTIFY_HOST` |  | Nutify host |
| `NUTIFY_HOST_NAME` |  | Nutify host name |
| `NUTIFY_LOGLEVEL` |  | Nutify loglevel |
| `NUTIFY_MEM_LIMIT` |  | Nutify mem limit |
| `NUTIFY_PORT` |  | Service port number |
| `NUTIFY_RESTART` |  | Container restart policy |
| `NUTIFY_SERVER_NAME` |  | Nutify server name |
| `NUTIFY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `NUTIFY_UPSCMD_PASSWORD` |  | Service password |
| `NUTIFY_UPSCMD_USER` |  | Service username |
| `NUTIFY_UPS_DRIVER` |  | Nutify ups driver |
| `NUTIFY_UPS_HOST` |  | Nutify ups host |
| `NUTIFY_UPS_NAME` |  | Nutify ups name |
| `NUTIFY_UPS_NOMINAL` |  | Nutify ups nominal |
| `NUTIFY_UPS_PASSWORD` |  | Service password |
| `NUTIFY_UPS_PORT` |  | Service port number |
| `NUTIFY_UPS_USER` |  | Service username |
| `NUTIFY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `NUTIFY_WERKZEUG` |  | Nutify werkzeug |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `3493:3493`

### Volumes
- `./etc/nutify/run:/var/run/nut` - Volume mount
- `./etc/nutify/logs:/app/nutify/logs` - Volume mount
- `./etc/nutify/instance:/app/nutify/instance` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${NUTIFY_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.nutify.entrypoints=websecure`
- `traefik.http.routers.nutify.rule=Host(`${NUTIFY_HOST_NAME:-nutify}.${HOST_DOMAIN}`)`
- `traefik.http.services.nutify.loadbalancer.server.port=5050`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NUTIFY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${NUTIFY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${NUTIFY_HOST_NAME:-nutify}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable nutify

# Configure environment variables (if needed)
make scaffold nutify

# Start the service
make up
```
