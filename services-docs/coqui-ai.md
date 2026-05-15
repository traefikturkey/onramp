# Coqui Ai

> Collection of ai models for speech recognition and synthesis

## Links
- [Official Repository](https://github.com/coqui-ai/TTS)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/coqui-ai.yml)

## Docker Images
- `ghcr.io/coqui-ai/tts-cpu:${COQUI_AI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COQUI_AI_CONTAINER_NAME` |  | Container name |
| `COQUI_AI_DOCKER_TAG` |  | Docker image tag/version |
| `COQUI_AI_RESTART` |  | Container restart policy |
| `COQUI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.coqui-ai.entrypoints=websecure`
- `traefik.http.routers.coqui-ai.rule=Host(`${COQUI_AI_CONTAINER_NAME:-coqui-ai}.${HOST_DOMAIN}`)`
- `traefik.http.services.coqui-ai.loadbalancer.server.port=5002`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${COQUI_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${COQUI_AI_CONTAINER_NAME:-coqui-ai}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable coqui-ai

# Configure environment variables (if needed)
make scaffold coqui-ai

# Start the service
make up
```
