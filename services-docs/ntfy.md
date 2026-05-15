# Ntfy

> Send push notifications to your phone or desktop using PUT/POST

## Links
- [Official Repository](https://github.com/binwiederhier/ntfy)
- [Official Documentation](https://docs.ntfy.sh/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/ntfy.yml)

## Docker Images
- `binwiederhier/ntfy:${NTFY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NTFY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `NTFY_CONTAINER_NAME` |  | Container name |
| `NTFY_DOCKER_TAG` |  | Docker image tag/version |
| `NTFY_HOST_NAME` |  | Ntfy host name |
| `NTFY_LOGIN` |  | Ntfy login |
| `NTFY_LOG_LEVEL` |  | Ntfy log level |
| `NTFY_MEM_LIMIT` |  | Ntfy mem limit |
| `NTFY_RESTART` |  | Container restart policy |
| `NTFY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `NTFY_UPSTREAM` |  | Ntfy upstream |
| `NTFY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `NTFY_WEB_PUSH_EMAIL` |  | Ntfy web push email |
| `NTFY_WP_PRIVATE_KEY` |  | Ntfy wp private key |
| `NTFY_WP_PUBLIC_KEY` |  | Ntfy wp public key |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/ntfy/config:/etc/ntfy` - Configuration files
- `./etc/ntfy/cache:/var/cache/ntfy` - Volume mount
- `./etc/ntfy/persistent:/var/lib/ntfy` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${NTFY_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.ntfy.entrypoints=websecure`
- `traefik.http.routers.ntfy.rule=Host(`${NTFY_HOST_NAME:-ntfy}.${HOST_DOMAIN}`)`
- `traefik.http.services.ntfy.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NTFY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${NTFY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${NTFY_HOST_NAME:-ntfy}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable ntfy

# Configure environment variables (if needed)
make scaffold ntfy

# Start the service
make up
```
