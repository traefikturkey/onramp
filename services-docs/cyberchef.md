# Cyberchef

> Web app for data analysis and transformation

## Links
- [Official Repository](https://github.com/gchq/CyberChef/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cyberchef.yml)

## Docker Images
- `ghcr.io/gchq/cyberchef:${CYBERCHEF_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CYBERCHEF_CONTAINER_NAME` |  | Container name |
| `CYBERCHEF_DOCKER_TAG` |  | Docker image tag/version |
| `CYBERCHEF_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.cyberchef.entrypoints=websecure`
- `traefik.http.routers.cyberchef.rule=Host(`${CYBERCHEF_CONTAINER_NAME:-cyberchef}.${HOST_DOMAIN}`)`
- `traefik.http.services.cyberchef.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CYBERCHEF_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${CYBERCHEF_CONTAINER_NAME:-cyberchef}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable cyberchef

# Configure environment variables (if needed)
make scaffold cyberchef

# Start the service
make up
```
