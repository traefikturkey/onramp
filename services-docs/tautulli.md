# Tautulli

> Monitors plex usage and provides statistics

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/tautulli)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/tautulli.yml)

## Docker Images
- `lscr.io/linuxserver/tautulli:${TAUTULLI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TAUTULLI_DOCKER_TAG` |  | Docker image tag/version |
| `TAUTULLI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/tautulli:/config` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.tautulli.entrypoints=websecure`
- `traefik.http.routers.tautulli.rule=Host(`tautulli.${HOST_DOMAIN}`)`
- `traefik.http.services.tautulli.loadbalancer.server.port=8181`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TAUTULLI_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=tautulli.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable tautulli

# Configure environment variables (if needed)
make scaffold tautulli

# Start the service
make up
```
