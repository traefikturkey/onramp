# Wireshark

> Network protocol analyzer

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/wireshark)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wireshark.yml)

## Docker Images
- `lscr.io/linuxserver/wireshark:${WIRESHARK_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WIRESHARK_CONTAINER_NAME` |  | Container name |
| `WIRESHARK_DOCKER_TAG` |  | Docker image tag/version |
| `WIRESHARK_RESTART` |  | Container restart policy |
| `WIRESHARK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `13000:3000`

### Volumes
- `./etc/wireshark:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.wireshark.entrypoints=websecure`
- `traefik.http.routers.wireshark.rule=Host(`${WIRESHARK_CONTAINER_NAME:-wireshark}.${HOST_DOMAIN}`)`
- `traefik.http.services.wireshark.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WIRESHARK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WIRESHARK_CONTAINER_NAME:-wireshark}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wireshark

# Configure environment variables (if needed)
make scaffold wireshark

# Start the service
make up
```
