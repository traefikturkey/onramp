# Librespeed

> Self-hosted internet speed test tool

## Links
- [Official Repository](https://github.com/linuxserver/docker-librespeed)
- [Docker Image](https://hub.docker.com/r/linuxserver/librespeed)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/librespeed.yml)

## Docker Images
- `lscr.io/linuxserver/librespeed:${LIBRESPEED_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `LIBRESPEED_CONTAINER_NAME` |  | Container name |
| `LIBRESPEED_DOCKER_TAG` |  | Docker image tag/version |
| `LIBRESPEED_PASSWORD` |  | Service password |
| `LIBRESPEED_RESTART` |  | Container restart policy |
| `LIBRESPEED_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/librespeed:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.librespeed.entrypoints=websecure`
- `traefik.http.routers.librespeed.rule=Host(`librespeed.${HOST_DOMAIN}`)`
- `traefik.http.services.librespeed.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LIBRESPEED_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=librespeed.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable librespeed

# Configure environment variables (if needed)
make scaffold librespeed

# Start the service
make up
```
