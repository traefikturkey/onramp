# Kasm

> Browser-based access to desktops, applications, and web services

## Links
- [Official Repository](https://github.com/linuxserver/docker-kasm)
- [Docker Image](https://hub.docker.com/r/linuxserver/kasm)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/kasm.yml)

## Docker Images
- `lscr.io/linuxserver/kasm:${KASM_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KASM_CONTAINER_NAME` |  | Container name |
| `KASM_DOCKER_TAG` |  | Docker image tag/version |
| `KASM_RESTART` |  | Container restart policy |
| `KASM_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/kasm/data:/opt` - Data storage
- `./etc/kasm/profiles:/profiles` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.kasm.entrypoints=websecure`
- `traefik.http.routers.kasm.rule=Host(`${KASM_CONTAINER_NAME:-kasm}.${HOST_DOMAIN}`)`
- `traefik.http.services.kasm.loadbalancer.server.port=443`
- `traefik.http.services.kasm.loadbalancer.server.scheme=https`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KASM_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${KASM_CONTAINER_NAME:-kasm}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable kasm

# Configure environment variables (if needed)
make scaffold kasm

# Start the service
make up
```
