# Pihole

> Network-wide ad blocker and dns sinkhole

## Links
- [Official Repository](https://github.com/pi-hole/docker-pi-hole/blob/master/README.md)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/pihole.yml)

## Docker Images
- `ghcr.io/pi-hole/pihole:${PIHOLE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PIHOLE_CONTAINER_NAME` |  | Container name |
| `PIHOLE_DOCKER_TAG` |  | Docker image tag/version |
| `PIHOLE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PIHOLE_WEBPASSWORD` |  | Service password |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `53:53/tcp`
- `53:53/udp`

### Volumes
- `./etc/pihole:/etc/pihole` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/pihole/dnsmasq:/etc/dnsmasq.d` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.middlewares.piholeredirect.redirectregex.regex=^https?://${PIHOLE_CONTAINER_NAME:-pihole}.${HOST_DOMAIN}/$$`
- `traefik.http.middlewares.piholeredirect.redirectregex.replacement=http://${PIHOLE_CONTAINER_NAME:-pihole}.${HOST_DOMAIN}/admin/`
- `traefik.http.routers.pihole.entrypoints=websecure`
- `traefik.http.routers.pihole.middlewares=piholeredirect`
- `traefik.http.routers.pihole.rule=Host(`${PIHOLE_CONTAINER_NAME:-pihole}.${HOST_DOMAIN}`)`
- `traefik.http.services.pihole.loadbalancer.server.port=443`
- `traefik.http.services.pihole.loadbalancer.server.scheme=https`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PIHOLE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PIHOLE_CONTAINER_NAME:-pihole}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### pihole-admin

**Purpose**: Alternative configuration for this service

**Changes**:
- **Adds/modifies services**: `pihole`

**Usage**:
```bash
make enable-override pihole-admin
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/pihole-admin.yml)

## Quick Start

```bash
# Enable the service
make enable pihole

# Configure environment variables (if needed)
make scaffold pihole

# Start the service
make up
```
