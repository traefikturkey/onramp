# Watcharr

> Self-hostable watched list

## Links
- [Official Documentation](https://watcharr.app/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/watcharr.yml)

## Docker Images
- `ghcr.io/sbondco/watcharr:${WATCHARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `WATCHARR_CONTAINER_NAME` |  | Container name |
| `WATCHARR_DOCKER_TAG` |  | Docker image tag/version |
| `WATCHARR_RESTART` |  | Container restart policy |
| `WATCHARR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/watcharr:/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.watcharr.entrypoints=websecure`
- `traefik.http.routers.watcharr.rule=Host(`${WATCHARR_CONTAINER_NAME:-watcharr}.${HOST_DOMAIN}`)`
- `traefik.http.services.watcharr.loadbalancer.server.port=3080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WATCHARR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WATCHARR_CONTAINER_NAME:-watcharr}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable watcharr

# Configure environment variables (if needed)
make scaffold watcharr

# Start the service
make up
```
