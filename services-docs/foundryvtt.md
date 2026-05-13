# Foundryvtt

> Virtual tabletop platform for role-playing games

## Links
- [Docker Image](https://hub.docker.com/r/felddy/foundryvtt)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/foundryvtt.yml)

## Docker Images
- `ghcr.io/felddy/foundryvtt:${FOUNDRYVTT_DOCKER_TAG:-release}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FOUNDRYVTT_ADMINKEY` | changeme | Foundryvtt adminkey |
| `FOUNDRYVTT_CONTAINER_NAME` | foundryvtt | Container name |
| `FOUNDRYVTT_DOCKER_TAG` | release | Docker image tag/version |
| `FOUNDRYVTT_PASSWORD` | changeme | Service password |
| `FOUNDRYVTT_RESTART` | unless-stopped | Container restart policy |
| `FOUNDRYVTT_USERNAME` | changeme | Service username |
| `FOUNDRYVTT_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/foundryvtt:/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.foundryvtt.entrypoints=websecure`
- `traefik.http.routers.foundryvtt.rule=Host(`${FOUNDRYVTT_CONTAINER_NAME:-foundryvtt}.${HOST_DOMAIN}`)`
- `traefik.http.services.foundryvtt.loadbalancer.server.port=30000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FOUNDRYVTT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FOUNDRYVTT_CONTAINER_NAME:-foundryvtt}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable foundryvtt

# Configure environment variables (if needed)
make scaffold foundryvtt

# Start the service
make up
```
