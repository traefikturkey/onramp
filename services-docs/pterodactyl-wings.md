# Pterodactyl Wings

> Daemon for managing game servers

## Links
- [Official Documentation](https://pterodactyl.io/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pterodactyl-wings.yml)

## Docker Images
- `<==== container_image ====>:${PTERODACTYL_WINGS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PTERODACTYL_WINGS_CONTAINER_NAME` |  | Container name |
| `PTERODACTYL_WINGS_DOCKER_TAG` |  | Docker image tag/version |
| `PTERODACTYL_WINGS_RESTART` |  | Container restart policy |
| `PTERODACTYL_WINGS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/pterodactyl-wings:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.pterodactyl-wings.entrypoints=websecure`
- `traefik.http.routers.pterodactyl-wings.rule=Host(`${PTERODACTYL_WINGS_CONTAINER_NAME:-pterodactyl-wings}.${HOST_DOMAIN}`)`
- `traefik.http.services.pterodactyl-wings.loadbalancer.server.port=8096`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PTERODACTYL_WINGS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PTERODACTYL_WINGS_CONTAINER_NAME:-pterodactyl-wings}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pterodactyl-wings

# Configure environment variables (if needed)
make scaffold pterodactyl-wings

# Start the service
make up
```
