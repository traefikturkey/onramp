# Gluetun

> VPN Client for Docker Containers and More

## Links
- [Official Repository](https://github.com/qdm12/gluetun)
- [Docker Image](https://hub.docker.com/r/qmcgaw/gluetun)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/gluetun.yml)

## Docker Images
- `ghcr.io/qdm12/gluetun:${GLUETUN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GLUETUN_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `GLUETUN_CONTAINER_NAME` |  | Container name |
| `GLUETUN_DNS_ADDRESS` |  | Gluetun dns address |
| `GLUETUN_DOCKER_TAG` |  | Docker image tag/version |
| `GLUETUN_MEM_LIMIT` |  | Gluetun mem limit |
| `GLUETUN_OPENVPN_USER` |  | Service username |
| `GLUETUN_RESTART` |  | Container restart policy |
| `GLUETUN_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `GLUETUN_VPN_PROVIDER` |  | Gluetun vpn provider |
| `GLUETUN_VPN_TYPE` |  | Gluetun vpn type |
| `GLUETUN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `GLUETUN_WIREGUARD_ADDRESSES` |  | Gluetun wireguard addresses |
| `GLUETUN_WIREGUARD_PRIVATE_KEY` |  | Gluetun wireguard private key |
| `GLUETUN_WIREGUARD_SERVER_COUNTRIES` |  | Gluetun wireguard server countries |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/gluetun:/gluetun` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${GLUETUN_TRAEFIK_ENABLED:-false}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GLUETUN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${GLUETUN_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable gluetun

# Configure environment variables (if needed)
make scaffold gluetun

# Start the service
make up
```
