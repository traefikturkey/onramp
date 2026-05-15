# Snapdrop

> PairDrop - Web-based file sharing tool for local networks (Snapdrop fork with improvements)

## Links
- [Official Documentation](https://docs.linuxserver.io/images/docker-pairdrop/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/snapdrop.yml)

## Docker Images
- `lscr.io/linuxserver/pairdrop:${SNAPDROP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SNAPDROP_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `SNAPDROP_CONTAINER_NAME` |  | Container name |
| `SNAPDROP_DOCKER_TAG` |  | Docker image tag/version |
| `SNAPDROP_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `SNAPDROP_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/snapdrop:/config` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SNAPDROP_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.snapdrop.entrypoints=websecure`
- `traefik.http.routers.snapdrop.rule=Host(`${SNAPDROP_CONTAINER_NAME:-snapdrop}.${HOST_DOMAIN}`)`
- `traefik.http.services.snapdrop.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SNAPDROP_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${SNAPDROP_AUTOHEAL:-true}`
- `joyride.host.name=${SNAPDROP_CONTAINER_NAME:-snapdrop}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable snapdrop

# Configure environment variables (if needed)
make scaffold snapdrop

# Start the service
make up
```
