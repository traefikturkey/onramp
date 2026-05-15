# Pulse

> Proxmox Monitoring system for real-time metrics

## Links
- [Official Repository](https://github.com/rcourtman/Pulse)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pulse.yml)

## Docker Images
- `rcourtman/pulse:${PULSE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `PULSE_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `PULSE_CONTAINER_NAME` |  | Container name |
| `PULSE_DOCKER_TAG` |  | Docker image tag/version |
| `PULSE_HOST_NAME` |  | Pulse host name |
| `PULSE_MEM_LIMIT` |  | Pulse mem limit |
| `PULSE_RESTART` |  | Container restart policy |
| `PULSE_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `PULSE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/pulse:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${PULSE_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.pulse.entrypoints=websecure`
- `traefik.http.routers.pulse.rule=Host(`${PULSE_HOST_NAME:-pulse}.${HOST_DOMAIN}`)`
- `traefik.http.services.pulse.loadbalancer.server.port=7655`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PULSE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${PULSE_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${PULSE_HOST_NAME:-pulse}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable pulse

# Configure environment variables (if needed)
make scaffold pulse

# Start the service
make up
```
