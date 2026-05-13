# Rustdesk

> Remote desktop software

## Links
- [Official Documentation](https://rustdesk.com/docs/en/self-host/install/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/rustdesk.yml)

## Docker Images
- `ghcr.io/rustdesk/rustdesk-server:${RUSTDESK_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `RUSTDECK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `RUSTDESK_CONTAINER_NAME` |  | Container name |
| `RUSTDESK_DOCKER_TAG` |  | Docker image tag/version |
| `RUSTDESK_ID_CONTAINER_NAME` |  | Container name |
| `RUSTDESK_RELAY_CONTAINER_NAME` |  | Container name |
| `RUSTDESK_RESTART` |  | Container restart policy |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `21115:21115`
- `21116:21116`
- `21116:21116/udp`
- `21118:21118`
- `21117:21117`
- `21119:21119`

### Volumes
- `./etc/rustdesk:/root` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${RUSTDECK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${RUSTDESK_RELAY_CONTAINER_NAME:-rustdesk-relay}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `rustdesk-relay`

## Quick Start

```bash
# Enable the service
make enable rustdesk

# Configure environment variables (if needed)
make scaffold rustdesk

# Start the service
make up
```

## Notes
- Requires rustdesk-relay to be running
