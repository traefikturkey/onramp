# Lidify

> Music discovery tool that provides recommendations based on selected Lidarr artists, using Spotify or LastFM.

## Links
- [Official Repository](https://github.com/TheWicklowWolf/Lidify)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/lidify.yml)

## Docker Images
- `thewicklowwolf/lidify:${LIDIFY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `LIDIFY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `LIDIFY_CONTAINER_NAME` |  | Container name |
| `LIDIFY_DOCKER_TAG` |  | Docker image tag/version |
| `LIDIFY_HOST_NAME` |  | Lidify host name |
| `LIDIFY_LASTFM_API_KEY` |  | Lidify lastfm api key |
| `LIDIFY_LASTFM_API_SECRET` |  | Lidify lastfm api secret |
| `LIDIFY_MEM_LIMIT` |  | Lidify mem limit |
| `LIDIFY_RESTART` |  | Container restart policy |
| `LIDIFY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `LIDIFY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/lidify:/lidify/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${LIDIFY_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.lidify.entrypoints=websecure`
- `traefik.http.routers.lidify.rule=Host(`${LIDIFY_HOST_NAME:-lidify}.${HOST_DOMAIN}`)`
- `traefik.http.services.lidify.loadbalancer.server.port=5000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LIDIFY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${LIDIFY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${LIDIFY_HOST_NAME:-lidify}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable lidify

# Configure environment variables (if needed)
make scaffold lidify

# Start the service
make up
```
