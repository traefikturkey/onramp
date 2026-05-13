# Wikijs

> Self-hosted wiki platform

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/wikijs)
- [Official Documentation](https://docs.requarks.io/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wikijs.yml)

## Docker Images
- `lscr.io/linuxserver/wikijs:${WIKIJS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WIKIJS_CONTAINER_NAME` |  | Container name |
| `WIKIJS_DOCKER_TAG` |  | Docker image tag/version |
| `WIKIJS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/wikijs:/config` - Volume mount
- `./etc/wikijs:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.wikijs.entrypoints=websecure`
- `traefik.http.routers.wikijs.rule=Host(`${WIKIJS_CONTAINER_NAME:-wikijs}.${HOST_DOMAIN}`)`
- `traefik.http.services.wikijs.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WIKIJS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WIKIJS_CONTAINER_NAME:-wikijs}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wikijs

# Configure environment variables (if needed)
make scaffold wikijs

# Start the service
make up
```
