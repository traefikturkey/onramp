# Sablier

> Container for running sablier, a web-based timer

## Links
- [Official Repository](https://github.com/acouvreur/sablier)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/sablier.yml)

## Docker Images
- `ghcr.io/acouvreur/sablier:${SABLIER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SABLIER_CONTAINER_NAME` |  | Container name |
| `SABLIER_DOCKER_TAG` |  | Docker image tag/version |
| `SABLIER_RESTART` |  | Container restart policy |
| `SABLIER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/sablier:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.middlewares.dynamic.plugin.sablier.dynamic.theme=hacker-terminal`
- `traefik.http.middlewares.dynamic.plugin.sablier.names=sablier_whoami_1`
- `traefik.http.middlewares.dynamic.plugin.sablier.sablierUrl=http://sablier:10000`
- `traefik.http.middlewares.dynamic.plugin.sablier.sessionDuration=1m`
- `traefik.http.routers.sablier.entrypoints=websecure`
- `traefik.http.routers.sablier.rule=Host(`${SABLIER_CONTAINER_NAME:-sablier}.${HOST_DOMAIN}`)`
- `traefik.http.services.sablier.loadbalancer.server.port=10000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SABLIER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SABLIER_CONTAINER_NAME:-sablier}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable sablier

# Configure environment variables (if needed)
make scaffold sablier

# Start the service
make up
```
