# Basaran

> ( archived ) Container for running basaran, a lightweight LLM server

## Links
- [Official Repository](https://github.com/hyperonym/basaran)
- [Official Documentation](https://huggingface.co/bigscience/bloomz-560m)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/basaran.yml)

## Docker Images
- `ghcr.io/hyperonym/basaran:${BASARAN_DOCKER_TAG:-0.13.3}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASARAN_CONTAINER_NAME` |  | Container name |
| `BASARAN_DOCKER_TAG` |  | Docker image tag/version |
| `BASARAN_MODEL` |  | Basaran model |
| `BASARAN_RESTART` |  | Container restart policy |
| `BASARAN_SERVER_MODEL` |  | Basaran server model |
| `BASARAN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
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
- `traefik.http.routers.basaran.entrypoints=websecure`
- `traefik.http.routers.basaran.rule=Host(`${BASARAN_CONTAINER_NAME:-basaran}.${HOST_DOMAIN}`)`
- `traefik.http.services.basaran.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BASARAN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${BASARAN_CONTAINER_NAME:-basaran}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable basaran

# Configure environment variables (if needed)
make scaffold basaran

# Start the service
make up
```
