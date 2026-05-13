# Netbox

> Web-based ip address management (ipam) and data center infrastructure management (dcim) tool

## Links
- [Official Documentation](https://docs.linuxserver.io/images/docker-netbox)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/netbox.yml)

## Docker Images
- `lscr.io/linuxserver/netbox:${NETBOX_DOCKER_TAG:-latest}`
- `postgres:16.4`
- `redis:alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NETBOX_CONTAINER_NAME` |  | Container name |
| `NETBOX_DOCKER_TAG` |  | Docker image tag/version |
| `NETBOX_SUPERUSER_EMAIL` |  | Service username |
| `NETBOX_SUPERUSER_PASS` |  | Service username |
| `NETBOX_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PG_DB` |  | Pg db |
| `PG_DB_NETBOX` |  | Pg db netbox |
| `PG_PASS_NETBOX` |  | Pg pass netbox |
| `PG_USER` |  | Service username |
| `PG_USER_NETBOX` |  | Service username |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/netbox:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/netbox/postgresql:/var/lib/postgresql/data` - Volume mount
- `netbox-redis:/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`
- `traefik.http.routers.netbox.entrypoints=websecure`
- `traefik.http.routers.netbox.rule=Host(`${NETBOX_CONTAINER_NAME:-netbox}.${HOST_DOMAIN}`)`
- `traefik.http.routers.netbox.service=netbox`
- `traefik.http.services.netbox.loadbalancer.server.port=8000`
- `traefik.http.services.netbox.loadbalancer.server.scheme=http`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NETBOX_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${NETBOX_CONTAINER_NAME:-netbox}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `netbox-postgresql`
- `netbox-redis`

## Quick Start

```bash
# Enable the service
make enable netbox

# Configure environment variables (if needed)
make scaffold netbox

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires netbox-postgresql, netbox-redis to be running
