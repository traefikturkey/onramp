# Dozzle Path

> Path-based reverse proxy for dozzle

## Links
- [Official Repository](https://github.com/amir20/dozzle)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dozzle-path.yml)

## Docker Images
- `amir20/dozzle:${DOZZLE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOZZLE_BASE` |  | Dozzle base |
| `DOZZLE_CONTAINER_NAME` |  | Container name |
| `DOZZLE_DOCKER_TAG` |  | Docker image tag/version |
| `DOZZLE_LEVEL` |  | Dozzle level |
| `DOZZLE_RESTART` |  | Container restart policy |
| `DOZZLE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.dozzle.entrypoints=websecure`
- `traefik.http.routers.dozzle.rule=PathPrefix(`${DOZZLE_BASE:-/logs}`)`
- `traefik.http.services.dozzle.loadbalancer.server.port=8080`
- `traefik.http.services.dozzle.loadbalancer.server.scheme=http`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOZZLE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable dozzle-path

# Configure environment variables (if needed)
make scaffold dozzle-path

# Start the service
make up
```
