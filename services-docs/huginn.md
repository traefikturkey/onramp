# Huginn

> Create agents that monitor and act on your behalf

## Links
- [Official Repository](https://github.com/huginn/huginn)
- [Docker Image](https://hub.docker.com/r/huginn/huginn/)
- [Official Documentation](https://www.youtube.com/watch?v=PzyvTHrLmQk)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/huginn.yml)

## Docker Images
- `ghcr.io/huginn/huginn:${HUGINN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `HUGINN_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `HUGINN_CONTAINER_NAME` |  | Container name |
| `HUGINN_DOCKER_TAG` |  | Docker image tag/version |
| `HUGINN_EMAIL_FROM_ADDRESS` |  | Huginn email from address |
| `HUGINN_RESTART` |  | Container restart policy |
| `HUGINN_SKIP_INVITATION_CODE` |  | Huginn skip invitation code |
| `HUGINN_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `HUGINN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `huginn:/var/lib/mysql` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${HUGINN_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.huginn.entrypoints=websecure`
- `traefik.http.routers.huginn.rule=Host(`${HUGINN_CONTAINER_NAME:-huginn}.${HOST_DOMAIN}`)`
- `traefik.http.services.huginn.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${HUGINN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${HUGINN_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${HUGINN_CONTAINER_NAME:-huginn}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable huginn

# Configure environment variables (if needed)
make scaffold huginn

# Start the service
make up
```
