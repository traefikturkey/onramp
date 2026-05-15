# Code Server

> Runs visual studio code in a web browser

## Links
- [Official Repository](https://github.com/linuxserver/docker-code-server)
- [Official Documentation](https://docs.linuxserver.io/images/docker-code-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/code-server.yml)

## Docker Images
- `lscr.io/linuxserver/code-server:${CODE_SERVER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CODE_SERVER_CONTAINER_NAME` |  | Container name |
| `CODE_SERVER_DOCKER_TAG` |  | Docker image tag/version |
| `CODE_SERVER_RESTART` |  | Container restart policy |
| `CODE_SERVER_SUDO_PASSWORD` |  | Service password |
| `CODE_SERVER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/code-server:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.code-server.entrypoints=websecure`
- `traefik.http.routers.code-server.rule=Host(`${CODE_SERVER_CONTAINER_NAME:-code-server}.${HOST_DOMAIN}`)`
- `traefik.http.services.code-server.loadbalancer.server.port=8443`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CODE_SERVER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${CODE_SERVER_CONTAINER_NAME:-code-server}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable code-server

# Configure environment variables (if needed)
make scaffold code-server

# Start the service
make up
```
