# Requestrr

> Integrates with sonarr and radarr for requesting media content

## Links
- [Docker Image](https://hub.docker.com/r/darkalfx/requestrr)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/requestrr.yml)

## Docker Images
- `darkalfx/requestrr:${REQUESTRR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `REQUESTRR_DOCKER_TAG` |  | Docker image tag/version |
| `REQUESTRR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/requestrr:/root/config` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.requestrr.entrypoints=websecure`
- `traefik.http.routers.requestrr.rule=Host(`requestrr.${HOST_DOMAIN}`)`
- `traefik.http.services.requestrr.loadbalancer.server.port=4545`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${REQUESTRR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=requestrr.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable requestrr

# Configure environment variables (if needed)
make scaffold requestrr

# Start the service
make up
```
