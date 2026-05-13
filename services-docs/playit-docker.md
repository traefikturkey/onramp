# Playit Docker

> An agent to expose local game servers to the internet using playit proxy service.

## Links
- [Official Repository](https://github.com/playit-cloud/playit-agent)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/playit-docker.yml)

## Docker Images
- `ghcr.io/mafen/playit-docker:${PLAYIT_DOCKER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PGID` |  | Group ID for file permissions |
| `PLAYIT_DOCKER_CONFIG` |  | Playit docker config |
| `PLAYIT_DOCKER_CONTAINER_NAME` |  | Container name |
| `PLAYIT_DOCKER_DOCKER_TAG` |  | Docker image tag/version |
| `PLAYIT_DOCKER_RESTART` |  | Container restart policy |
| `PLAYIT_DOCKER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${PLAYIT_DOCKER_CONFIG:-./etc/playit-docker}` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PLAYIT_DOCKER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable playit-docker

# Configure environment variables (if needed)
make scaffold playit-docker

# Start the service
make up
```
