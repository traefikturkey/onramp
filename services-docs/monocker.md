# Monocker

> Monitors container states, and sends notifications at state change

## Links
- [Official Repository](https://github.com/petersem/monocker)
- [Docker Image](https://hub.docker.com/r/petersem/monocker)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/monocker.yml)

## Docker Images
- `petersem/monocker:${MONOCKER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MONOCKER_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `MONOCKER_CONTAINER_NAME` | monocker | Container name |
| `MONOCKER_DOCKER_TAG` | latest | Docker image tag/version |
| `MONOCKER_EXCLUDE_EXITED` | false | Monocker exclude exited |
| `MONOCKER_LABEL_ENABLE` | false | Monocker label enable |
| `MONOCKER_MEM_LIMIT` | 130m | Monocker mem limit |
| `MONOCKER_MESSAGE_PLATFORM` | ${MONOCKER_MESSAGE_PLATFORM:-} | Monocker message platform |
| `MONOCKER_ONLY_OFFLINE_STATES` | false | Monocker only offline states |
| `MONOCKER_RESTART` | unless-stopped | Container restart policy |
| `MONOCKER_SERVER_LABEL` | ${HOST_NAME | Monocker server label |
| `MONOCKER_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `MONOCKER_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=${MONOCKER_TRAEFIK_ENABLE:-true}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MONOCKER_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${MONOCKER_AUTOHEAL:-true}`

## Quick Start

```bash
# Enable the service
make enable monocker

# Configure environment variables (if needed)
make scaffold monocker

# Start the service
make up
```
