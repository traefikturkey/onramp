# Cadvisor

> Collects and analyzes resource usage and performance characteristics of running containers

## Links
- [Official Repository](https://github.com/google/cadvisor)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cadvisor.yml)

## Docker Images
- `gcr.io/cadvisor/cadvisor:${CADVISOR_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CADVISOR_CONTAINER_NAME` |  | Container name |
| `CADVISOR_DOCKER_TAG` |  | Docker image tag/version |
| `CADVISOR_RESTART` |  | Container restart policy |
| `CADVISOR_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Volumes
- `/:/rootfs` - Volume mount
- `/sys:/sys` - Volume mount
- `/sys/fs/cgroup:/cgroup` - Volume mount
- `/dev/disk/:/dev/disk` - Volume mount
- `/var/run:/var/run` - Volume mount
- `/var/lib/docker/:/var/lib/docker` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.cadvisor.entrypoints=websecure`
- `traefik.http.routers.cadvisor.rule=Host(`${CADVISOR_CONTAINER_NAME:-cadvisor}.${HOST_DOMAIN}`)`
- `traefik.http.services.cadvisor.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CADVISOR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `joyride.host.name=${CADVISOR_CONTAINER_NAME:-cadvisor}.${HOST_DOMAIN}`
- `org.label-schema.group=monitoring`

## Quick Start

```bash
# Enable the service
make enable cadvisor

# Configure environment variables (if needed)
make scaffold cadvisor

# Start the service
make up
```
