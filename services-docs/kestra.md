# Kestra

> Event Driven Orchestration & Scheduling Platform

## Links
- [Official Repository](https://github.com/kestra-io/kestra/blob/develop/docker-compose.yml)
- [Official Documentation](https://kestra.io/docs)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/kestra.yml)

## Docker Images
- `ghcr.io/kestra-io/kestra:${KESTRA_DOCKER_TAG:-latest-full}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KESTRA_COMMAND` |  | Kestra command |
| `KESTRA_CONTAINER_NAME` |  | Container name |
| `KESTRA_DOCKER_TAG` |  | Docker image tag/version |
| `KESTRA_RESTART` |  | Container restart policy |
| `KESTRA_USER` |  | Service username |
| `KESTRA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `4040:8080`

### Volumes
- `./etc/kestra/storage:/app/storage` - Volume mount
- `/tmp/kestra-wd:/tmp` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.kestra.entrypoints=websecure`
- `traefik.http.routers.kestra.rule=Host(`${KESTRA_CONTAINER_NAME:-kestra}.${HOST_DOMAIN}`)`
- `traefik.http.services.kestra.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KESTRA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${KESTRA_CONTAINER_NAME:-kestra}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable kestra

# Configure environment variables (if needed)
make scaffold kestra

# Start the service
make up
```
