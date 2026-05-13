# Recyclarr

> Container for running recyclarr, a media indexer

## Links
- [Official Repository](https://github.com/recyclarr/recyclarr#)
- [Docker Image](https://hub.docker.com/r/recyclarr/recyclarr)
- [Official Documentation](https://recyclarr.dev/wiki/installation/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/recyclarr.yml)

## Docker Images
- `ghcr.io/recyclarr/recyclarr:${RECYCLARR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `RECYCLARR_CONTAINER_NAME` |  | Container name |
| `RECYCLARR_DOCKER_TAG` |  | Docker image tag/version |
| `RECYCLARR_RESTART` |  | Container restart policy |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/recyclarr:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=false`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable recyclarr

# Configure environment variables (if needed)
make scaffold recyclarr

# Start the service
make up
```
