# Synchronet

> Synchronet BBS

## Links
- [Docker Image](https://hub.docker.com/r/bbsio/synchronet)
- [Official Documentation](https://wiki.synchro.net/index)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/synchronet.yml)

## Docker Images
- `bbsio/synchronet:${SYNCHRONET_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SYNCHRONET_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `SYNCHRONET_CONTAINER_NAME` |  | Container name |
| `SYNCHRONET_DOCKER_TAG` |  | Docker image tag/version |
| `SYNCHRONET_MEM_LIMIT` |  | Synchronet mem limit |
| `SYNCHRONET_RESTART` |  | Container restart policy |
| `SYNCHRONET_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `SYNCHRONET_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `1123:1123`
- `11235:11235`
- `21:21`
- `2222:22`
- `23:23`
- `513:513`
- `64:64`
- `128:128`
- `25:25`
- `587:587`
- `465:465`
- `110:110`
- `995:995`
- `119:119`
- `563:563`
- `18:18`
- `11:11`
- `17:17`
- `79:79`
- `6667:6667`

### Volumes
- `./etc/synchronet:/sbbs-data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SYNCHRONET_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.synchronet.entrypoints=websecure`
- `traefik.http.routers.synchronet.rule=Host(`${SYNCHRONET_CONTAINER_NAME:-synchronet}.${HOST_DOMAIN}`)`
- `traefik.http.services.synchronet.loadbalancer.server.port=443`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SYNCHRONET_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${SYNCHRONET_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${SYNCHRONET_CONTAINER_NAME:-synchronet}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable synchronet

# Configure environment variables (if needed)
make scaffold synchronet

# Start the service
make up
```
