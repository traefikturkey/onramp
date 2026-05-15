# Databasus

> Self-hosted database backup tool with S3, Google Drive, FTP storage and Slack, Discord, Telegram notifications

## Links
- [Official Repository](https://github.com/databasus/databasus)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/databasus.yml)

## Docker Images
- `databasus/databasus:${DATABASUS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASUS_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `DATABASUS_CONTAINER_NAME` | databasus | Container name |
| `DATABASUS_DOCKER_TAG` | latest | Docker image tag/version |
| `DATABASUS_RESTART` | unless-stopped | Container restart policy |
| `DATABASUS_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `DATABASUS_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/databasus:/databasus-data` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${DATABASUS_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.databasus.entrypoints=websecure`
- `traefik.http.routers.databasus.rule=Host(`${DATABASUS_CONTAINER_NAME:-databasus}.${HOST_DOMAIN}`)`
- `traefik.http.services.databasus.loadbalancer.server.port=4005`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DATABASUS_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${DATABASUS_AUTOHEAL:-true}`
- `joyride.host.name=${DATABASUS_CONTAINER_NAME:-databasus}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable databasus

# Configure environment variables (if needed)
make scaffold databasus

# Start the service
make up
```
