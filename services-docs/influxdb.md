# Influxdb

> Time-series database for metrics and events

## Links
- [Official Repository](https://github.com/influxdata/influxdb)
- [Docker Image](https://hub.docker.com/_/influxdb)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/influxdb.yml)

## Docker Images
- `influxdb:${INFLUXDB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `INFLUXDB_CONTAINER_NAME` | influxdb | Container name |
| `INFLUXDB_DIR` | ./media/databases/influxdb | Influxdb dir |
| `INFLUXDB_DOCKER_TAG` | latest | Docker image tag/version |
| `INFLUXDB_INIT_ADMIN_PASSWORD` |  | Service password |
| `INFLUXDB_INIT_ADMIN_TOKEN` |  | Influxdb init admin token |
| `INFLUXDB_INIT_ADMIN_USER` | admin | Service username |
| `INFLUXDB_INIT_BUCKET` | default | Influxdb init bucket |
| `INFLUXDB_INIT_ORG` | homelab | Influxdb init org |
| `INFLUXDB_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/influxdb:/etc/influxdb2` - Volume mount
- `${INFLUXDB_DIR:-./media/databases/influxdb}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.influxdb.entrypoints=websecure`
- `traefik.http.routers.influxdb.rule=Host(`${INFLUXDB_CONTAINER_NAME:-influxdb}.${HOST_DOMAIN}`)`
- `traefik.http.services.influxdb.loadbalancer.server.port=8086`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${INFLUXDB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${INFLUXDB_CONTAINER_NAME:-influxdb}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable influxdb

# Configure environment variables (if needed)
make scaffold influxdb

# Start the service
make up
```
