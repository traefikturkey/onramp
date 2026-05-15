# Wetty

> Terminal in browser over http/https.

## Links
- [Official Repository](https://github.com/butlerx/wetty)
- [Official Documentation](https://linuxiac.com/how-to-set-up-web-based-ssh/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wetty.yml)

## Docker Images
- `wettyoss/wetty:${WETTY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WETTY_ALLOW_IFRAME` |  | Wetty allow iframe |
| `WETTY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `WETTY_BASE` |  | Wetty base |
| `WETTY_COMMAND` |  | Wetty command |
| `WETTY_CONTAINER_NAME` |  | Container name |
| `WETTY_DOCKER_TAG` |  | Docker image tag/version |
| `WETTY_MEM_LIMIT` |  | Wetty mem limit |
| `WETTY_RESTART` |  | Container restart policy |
| `WETTY_SSH_AUTH` |  | Wetty ssh auth |
| `WETTY_SSH_CONTAINER_KEYFILE` |  | Wetty ssh container keyfile |
| `WETTY_SSH_HOST` |  | Wetty ssh host |
| `WETTY_SSH_HOST_KEYFILE` |  | Wetty ssh host keyfile |
| `WETTY_SSH_PASS` |  | Wetty ssh pass |
| `WETTY_SSH_PORT` |  | Service port number |
| `WETTY_SSH_USER` |  | Service username |
| `WETTY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `WETTY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `${WETTY_SSH_HOST_KEYFILE:-/home/${USER}/.ssh/id_ed25519}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${WETTY_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.wetty.entrypoints=websecure`
- `traefik.http.routers.wetty.rule=Host(`${WETTY_CONTAINER_NAME:-wetty}.${HOST_DOMAIN}`)`
- `traefik.http.services.wetty.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WETTY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${WETTY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${WETTY_CONTAINER_NAME:-wetty}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wetty

# Configure environment variables (if needed)
make scaffold wetty

# Start the service
make up
```
