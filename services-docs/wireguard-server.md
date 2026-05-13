# Wireguard Server

> Vpn server using wireguard

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/wireguard)
- [Official Documentation](https://docs.linuxserver.io/images/docker-wireguard)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wireguard-server.yml)

## Docker Images
- `lscr.io/linuxserver/wireguard:${WIREGUARD_SERVER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WIREGUARD_ALLOWEDIPS` |  | Wireguard allowedips |
| `WIREGUARD_INTERNAL_SUBNET` |  | Wireguard internal subnet |
| `WIREGUARD_PEERDNS` |  | Wireguard peerdns |
| `WIREGUARD_PEERS` |  | Wireguard peers |
| `WIREGUARD_SERVER_CONTAINER_NAME` |  | Container name |
| `WIREGUARD_SERVER_DOCKER_TAG` |  | Docker image tag/version |
| `WIREGUARD_SERVER_PORT` |  | Service port number |
| `WIREGUARD_SERVER_RESTART` |  | Container restart policy |
| `WIREGUARD_SERVER_URL` |  | Wireguard server url |
| `WIREGUARD_SERVER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `${WIREGUARD_SERVER_PORT:-51820}:${WIREGUARD_SERVER_PORT:-51820}/udp`

### Volumes
- `./etc/wireguard-server:/config` - Volume mount
- `/lib/modules:/lib/modules` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WIREGUARD_SERVER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WIREGUARD_SERVER_CONTAINER_NAME:-wireguard-server}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wireguard-server

# Configure environment variables (if needed)
make scaffold wireguard-server

# Start the service
make up
```
