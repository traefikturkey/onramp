# Transmission Vpn

> Bittorrent client with vpn support

## Links
- [Docker Image](https://hub.docker.com/r/haugene/transmission-openvpn)
- [Official Documentation](https://haugene.github.io/docker-transmission-openvpn/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/transmission-vpn.yml)

## Docker Images
- `haugene/transmission-openvpn:${TRANSMISSION_VPN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TRANSMISSION_VPN_CONFIG` |  | Transmission vpn config |
| `TRANSMISSION_VPN_CONTAINER_NAME` |  | Container name |
| `TRANSMISSION_VPN_DOCKER_TAG` |  | Docker image tag/version |
| `TRANSMISSION_VPN_LOCAL_NETWORK` |  | Transmission vpn local network |
| `TRANSMISSION_VPN_PASSWORD` |  | Service password |
| `TRANSMISSION_VPN_PROVIDER` |  | Transmission vpn provider |
| `TRANSMISSION_VPN_USERNAME` |  | Service username |
| `TRANSMISSION_VPN_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TRANSMISSION_WEBUI` |  | Transmission webui |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `9091:9091`

### Volumes
- `./etc/transmission-vpn:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=true`
- `traefik.http.routers.transmission-vpn.entrypoints=websecure`
- `traefik.http.routers.transmission-vpn.rule=Host(`${TRANSMISSION_VPN_CONTAINER_NAME:-transmission-vpn}.${HOST_DOMAIN}`)`
- `traefik.http.services.transmission-vpn.loadbalancer.server.port=9091`
- `traefik.http.services.transmission-vpn.loadbalancer.server.scheme=http`
- `traefik.passHostHeader=true`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TRANSMISSION_VPN_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${TRANSMISSION_VPN_CONTAINER_NAME:-transmission-vpn}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable transmission-vpn

# Configure environment variables (if needed)
make scaffold transmission-vpn

# Start the service
make up
```
