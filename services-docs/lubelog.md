# Lubelog

> Self-Hosted, Open-Source, Web-Based Vehicle Maintenance and Fuel Mileage Tracker

## Links
- [Official Repository](https://github.com/hargata/lubelog)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/lubelog.yml)

## Docker Images
- `ghcr.io/hargata/lubelogger:${LUBELOG_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `LUBELOG_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `LUBELOG_CONTAINER_NAME` |  | Container name |
| `LUBELOG_DOCKER_TAG` |  | Docker image tag/version |
| `LUBELOG_LANG` |  | Lubelog lang |
| `LUBELOG_LC_ALL` |  | Lubelog lc all |
| `LUBELOG_LOG_LEVEL` |  | Lubelog log level |
| `LUBELOG_MAIL_FROM` |  | Lubelog mail from |
| `LUBELOG_MAIL_PASSWORD` |  | Service password |
| `LUBELOG_MAIL_PORT` |  | Service port number |
| `LUBELOG_MAIL_SERVER` |  | Lubelog mail server |
| `LUBELOG_MAIL_USERNAME` |  | Service username |
| `LUBELOG_MAIL_USE_SSL` |  | Lubelog mail use ssl |
| `LUBELOG_MEM_LIMIT` |  | Lubelog mem limit |
| `LUBELOG_RESTART` |  | Container restart policy |
| `LUBELOG_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `LUBELOG_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/lubelog/config:/App/config` - Configuration files
- `./etc/lubelog/data:/App/data` - Data storage
- `./etc/lubelog/translations:/App/wwwroot/translations` - Volume mount
- `./etc/lubelog/documents:/App/wwwroot/documents` - Volume mount
- `./etc/lubelog/images:/App/wwwroot/images` - Volume mount
- `./etc/lubelog/temp:/App/wwwroot/temp` - Volume mount
- `./etc/lubelog/log:/App/log` - Volume mount
- `./etc/lubelog/keys:/root/.aspnet/DataProtection-Keys` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${LUBELOG_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.lubelog.entrypoints=websecure`
- `traefik.http.routers.lubelog.rule=Host(`${LUBELOG_CONTAINER_NAME:-lubelog}.${HOST_DOMAIN}`)`
- `traefik.http.services.lubelog.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LUBELOG_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${LUBELOG_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${LUBELOG_CONTAINER_NAME:-lubelog}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable lubelog

# Configure environment variables (if needed)
make scaffold lubelog

# Start the service
make up
```
