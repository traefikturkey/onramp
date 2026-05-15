# Onramp Dashboard

> Web dashboard for OnRamp homelab management

## Links
- [Official Repository](https://github.com/your-repo/onramp)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/onramp-dashboard.yml)

## Docker Images
- `sietch`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `ONRAMP_DASHBOARD_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `ONRAMP_DASHBOARD_CONTAINER_NAME` | onramp-dashboard | Container name |
| `ONRAMP_DASHBOARD_DEBUG` | false | Onramp dashboard debug |
| `ONRAMP_DASHBOARD_HOST_NAME` | dashboard | Onramp dashboard host name |
| `ONRAMP_DASHBOARD_MEM_LIMIT` | 256m | Onramp dashboard mem limit |
| `ONRAMP_DASHBOARD_RESTART` | unless-stopped | Container restart policy |
| `ONRAMP_DASHBOARD_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `ONRAMP_DASHBOARD_WATCHTOWER` | true | Onramp dashboard watchtower |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./services-available:/app/services-available` - Volume mount
- `./services-scaffold:/app/services-scaffold` - Volume mount
- `./Makefile:/app/Makefile` - Volume mount
- `./make.d:/app/make.d` - Volume mount
- `./services-enabled:/app/services-enabled` - Volume mount
- `./etc:/app/etc` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${ONRAMP_DASHBOARD_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.onramp-dashboard.entrypoints=websecure`
- `traefik.http.routers.onramp-dashboard.rule=Host(`${ONRAMP_DASHBOARD_HOST_NAME:-dashboard}.${HOST_DOMAIN}`)`
- `traefik.http.services.onramp-dashboard.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ONRAMP_DASHBOARD_WATCHTOWER:-true}`

**Other Labels:**
- `autoheal=${ONRAMP_DASHBOARD_AUTOHEAL:-true}`
- `joyride.host.name=${ONRAMP_DASHBOARD_HOST_NAME:-dashboard}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable onramp-dashboard

# Configure environment variables (if needed)
make scaffold onramp-dashboard

# Start the service
make up
```
