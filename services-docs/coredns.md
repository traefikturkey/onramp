# Coredns

> A fast and flexible DNS server with plugin support

## Links
- [Official Repository](https://github.com/coredns/coredns/blob/master/coredns.1.md)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/coredns.yml)

## Docker Images
- `coredns/coredns:${COREDNS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COREDNS_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `COREDNS_CONFIG` | Corefile | Coredns config |
| `COREDNS_CONTAINER_NAME` |  | Container name |
| `COREDNS_DOCKER_TAG` | latest | Docker image tag/version |
| `COREDNS_MEM_LIMIT` |  | Coredns mem limit |
| `COREDNS_PORT` | 53 | Service port number |
| `COREDNS_RELOAD` | 10s | Coredns reload |
| `COREDNS_RESTART` |  | Container restart policy |
| `COREDNS_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `COREDNS_UPSTREAM_SERVER_1` | 1.1.1.1 | Coredns upstream server 1 |
| `COREDNS_UPSTREAM_SERVER_2` | 9.9.9.9 | Coredns upstream server 2 |
| `COREDNS_UPSTREAM_SERVER_3` | 8.8.8.8 | Coredns upstream server 3 |
| `COREDNS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOSTIP` |  | Hostip |
| `HOST_DOMAIN` |  | Host domain for service access |
| `HOST_NAME` |  | Host name |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${COREDNS_PORT:-53}:53/udp`
- `${COREDNS_PORT:-53}:53/tcp`

### Volumes
- `./etc/coredns:/config` - Volume mount
- `./etc/coredns/hosts:/etc/hosts` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${COREDNS_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.coredns.entrypoints=websecure`
- `traefik.http.routers.coredns.rule=Host(`${COREDNS_CONTAINER_NAME:-coredns}.${HOST_DOMAIN}`)`
- `traefik.http.services.coredns.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${COREDNS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${COREDNS_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${COREDNS_CONTAINER_NAME:-coredns}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable coredns

# Configure environment variables (if needed)
make scaffold coredns

# Start the service
make up
```
