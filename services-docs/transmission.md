# Transmission

> Transmission bittorrent client with no VPN. Intended to be used with Gluetun.

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/transmission)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/transmission.yml)

## Docker Images
- `lscr.io/linuxserver/transmission:${TRANSMISSION_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TRANSMISSION_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `TRANSMISSION_CONTAINER_NAME` |  | Container name |
| `TRANSMISSION_DOCKER_TAG` |  | Docker image tag/version |
| `TRANSMISSION_HOST_NAME` |  | Transmission host name |
| `TRANSMISSION_HOST_WHITELIST` |  | Transmission host whitelist |
| `TRANSMISSION_MEM_LIMIT` |  | Transmission mem limit |
| `TRANSMISSION_PASSWORD` |  | Service password |
| `TRANSMISSION_PEERPORT` |  | Service port number |
| `TRANSMISSION_RESTART` |  | Container restart policy |
| `TRANSMISSION_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `TRANSMISSION_USER` |  | Service username |
| `TRANSMISSION_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TRANSMISSION_WEB_HOME` |  | Transmission web home |
| `TRANSMISSION_WHITELIST` |  | Transmission whitelist |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/transmission:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/transmission/downloads:/downloads` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${TRANSMISSION_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.transmission.entrypoints=websecure`
- `traefik.http.routers.transmission.rule=Host(`${TRANSMISSION_HOST_NAME:-transmission}.${HOST_DOMAIN}`)`
- `traefik.http.services.transmission.loadbalancer.server.port=9091`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TRANSMISSION_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${TRANSMISSION_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${TRANSMISSION_HOST_NAME:-transmission}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable transmission

# Configure environment variables (if needed)
make scaffold transmission

# Start the service
make up
```
