# Wg Easy

> Wireguard vpn configuration generator and server

## Links
- [Official Repository](https://github.com/WeeJeWel/wg-easy)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wg-easy.yml)

## Docker Images
- `ghcr.io/wg-easy/wg-easy:${WG_EASY_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WG_EASY_ALLOWED_IPS` | 10.8.0.0/24 | Wg easy allowed ips |
| `WG_EASY_CONTAINER_NAME` | wg-easy | Container name |
| `WG_EASY_DOCKER_TAG` | latest | Docker image tag/version |
| `WG_EASY_HOST` | ${HOST_DOMAIN} | Wg easy host |
| `WG_EASY_RESTART` | unless-stopped | Container restart policy |
| `WG_EASY_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |

## Configuration

### Ports
- `51820:51820/udp`

### Volumes
- `./etc/wg-easy:/etc/wireguard` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.wg-easy.entrypoints=websecure`
- `traefik.http.routers.wg-easy.rule=Host(`${WG_EASY_CONTAINER_NAME:-wg-easy}.${HOST_DOMAIN}`)`
- `traefik.http.services.wg-easy.loadbalancer.server.port=51821`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WG_EASY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WG_EASY_CONTAINER_NAME:-wg-easy}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable wg-easy

# Configure environment variables (if needed)
make scaffold wg-easy

# Start the service
make up
```
