# Unifi

> Network management controller for ubiquiti devices

## Links
- [Official Repository](https://github.com/goofball222/unifi)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/unifi.yml)

## Docker Images
- `ghcr.io/goofball222/unifi:${UNIFI_DOCKER_TAG:-latest-ubuntu}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `UNIFI_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `UNIFI_AUTOHEAL_TIMEOUT` |  | Enable Autoheal container restart on unhealthy status |
| `UNIFI_CONTAINER_NAME` |  | Container name |
| `UNIFI_DOCKER_TAG` |  | Docker image tag/version |
| `UNIFI_MEM_LIMIT` |  | Unifi mem limit |
| `UNIFI_RESTART` |  | Container restart policy |
| `UNIFI_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `UNIFI_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `3478:3478/udp`
- `5514:5514/udp`
- `6789:6789`
- `8080:8080`
- `10001:10001/udp`

### Volumes
- `./etc/unifi/data:/usr/lib/unifi/data` - Data storage
- `./etc/unifi/cert:/usr/lib/unifi/cert` - Volume mount
- `./etc/unifi/logs:/usr/lib/unifi/logs` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${UNIFI_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.unifi.entrypoints=websecure`
- `traefik.http.routers.unifi.rule=Host(`${UNIFI_CONTAINER_NAME:-unifi}.${HOST_DOMAIN}`)`
- `traefik.http.services.unifi.loadbalancer.server.port=8443`
- `traefik.http.services.unifi.loadbalancer.server.scheme=https`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${UNIFI_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${UNIFI_AUTOHEAL:-true}`
- `autoheal.stop.timeout=${UNIFI_AUTOHEAL_TIMEOUT:-180}`
- `joyride.host.name=${UNIFI_CONTAINER_NAME:-unifi}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable unifi

# Configure environment variables (if needed)
make scaffold unifi

# Start the service
make up
```
