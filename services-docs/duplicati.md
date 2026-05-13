# Duplicati

> Backs up files and folders to various storage destinations

## Links
- [Official Documentation](https://www.duplicati.com/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/duplicati.yml)

## Docker Images
- `lscr.io/linuxserver/duplicati:${DUPLICATI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DUPLICATI_CONTAINER_NAME` |  | Container name |
| `DUPLICATI_DOCKER_TAG` |  | Docker image tag/version |
| `DUPLICATI_HOST_NAME` |  | Duplicati host name |
| `DUPLICATI_PASS` |  | Duplicati pass |
| `DUPLICATI_RESTART` |  | Container restart policy |
| `DUPLICATI_SETTINGS_ENCRYPTION_KEY` |  | Duplicati settings encryption key |
| `DUPLICATI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/duplicati:/config` - Volume mount
- `./media/backups:/backups` - Volume mount
- `./:/mnt/onramp` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.duplicati.entrypoints=websecure`
- `traefik.http.routers.duplicati.rule=Host(`${DUPLICATI_HOST_NAME:-duplicati}.${HOST_DOMAIN}`)`
- `traefik.http.services.duplicati.loadbalancer.server.port=8200`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DUPLICATI_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${DUPLICATI_HOST_NAME:-duplicati}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable duplicati

# Configure environment variables (if needed)
make scaffold duplicati

# Start the service
make up
```
