# Pterodactyl Panel

> Game server management panel

## Links
- [Official Repository](https://github.com/EdyTheCow/docker-pterodactyl/blob/master/panel/compose/docker-compose.yml)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pterodactyl-panel.yml)

## Docker Images
- `ghcr.io/pterodactyl/panel:${PTERODACTYL_PANEL_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PTERODACTYL_PANEL_CONTAINER_NAME` |  | Container name |
| `PTERODACTYL_PANEL_DB_DATABASE` |  | Pterodactyl panel db database |
| `PTERODACTYL_PANEL_DB_PASSWORD` |  | Service password |
| `PTERODACTYL_PANEL_DB_USERNAME` |  | Service username |
| `PTERODACTYL_PANEL_DOCKER_TAG` |  | Docker image tag/version |
| `PTERODACTYL_PANEL_RECAPTCHA_ENABLED` |  | Pterodactyl panel recaptcha enabled |
| `PTERODACTYL_PANEL_RESTART` |  | Container restart policy |
| `PTERODACTYL_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/pterodactyl-panel:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/pterodactyl-panel/var/:/app/var/` - Volume mount
- `./etc/pterodactyl-panel/logs/:/app/storage/logs` - Volume mount
- `./etc/pterodactyl-panel/nginx/:/etc/nginx/conf.d/` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.pterodactyl-panel.entrypoints=websecure`
- `traefik.http.routers.pterodactyl-panel.rule=Host(`${PTERODACTYL_PANEL_CONTAINER_NAME:-panel}.${HOST_DOMAIN}`)`
- `traefik.http.services.pterodactyl-panel.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PTERODACTYL_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PTERODACTYL_PANEL_CONTAINER_NAME:-panel}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pterodactyl-panel

# Configure environment variables (if needed)
make scaffold pterodactyl-panel

# Start the service
make up
```
