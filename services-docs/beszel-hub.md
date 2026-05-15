# Beszel Hub

> lightweight server monitoring platform that includes Docker statistics, historical data, and alert functions.

## Links
- [Official Repository](https://github.com/henrygd/beszel)
- [Official Documentation](https://beszel.dev)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/beszel-hub.yml)

## Docker Images
- `ghcr.io/henrygd/beszel/beszel:${BESZEL_HUB_DOCKER_TAG:-latest}`
- `ghcr.io/henrygd/beszel/beszel-agent:${BESZEL_AGENT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BESZEL_AGENT_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `BESZEL_AGENT_CONTAINER_NAME` |  | Container name |
| `BESZEL_AGENT_DOCKER_TAG` |  | Docker image tag/version |
| `BESZEL_AGENT_RESTART` |  | Container restart policy |
| `BESZEL_AGENT_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `BESZEL_AGENT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `BESZEL_HUB_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `BESZEL_HUB_CONTAINER_NAME` |  | Container name |
| `BESZEL_HUB_DOCKER_TAG` |  | Docker image tag/version |
| `BESZEL_HUB_HOST_NAME` |  | Beszel hub host name |
| `BESZEL_HUB_RESTART` |  | Container restart policy |
| `BESZEL_HUB_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `BESZEL_HUB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `BESZEL_PUBLIC_KEY` |  | Beszel public key |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/beszel-hub/data:/beszel_data` - Data storage
- `./etc/beszel-hub/socket:/beszel_socket` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${BESZEL_AGENT_TRAEFIK_ENABLED:-false}`
- `traefik.http.routers.beszel-hub.entrypoints=websecure`
- `traefik.http.routers.beszel-hub.rule=Host(`${BESZEL_HUB_HOST_NAME:-beszel}.${HOST_DOMAIN}`)`
- `traefik.http.services.beszel-hub.loadbalancer.server.port=8090`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BESZEL_AGENT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${BESZEL_AGENT_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${BESZEL_HUB_HOST_NAME:-beszel}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable beszel-hub

# Configure environment variables (if needed)
make scaffold beszel-hub

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
