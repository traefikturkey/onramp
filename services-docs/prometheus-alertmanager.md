# Prometheus Alertmanager

> Manages alerts from prometheus monitoring

## Links
- [Official Repository](https://github.com/prometheus/alertmanager)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prometheus-alertmanager.yml)

## Docker Images
- `prom/alertmanager:${ALERTMANAGER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALERTMANAGER_CONTAINER_NAME` |  | Container name |
| `ALERTMANAGER_DOCKER_TAG` |  | Docker image tag/version |
| `ALERTMANAGER_HOST_NAME` |  | Alertmanager host name |
| `ALERTMANAGER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Volumes
- `./etc/prometheus/conf:/etc/alertmanager` - Volume mount
- `prometheus:/alertmanager` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.alertmanager.entrypoints=websecure`
- `traefik.http.routers.alertmanager.rule=Host(`${ALERTMANAGER_HOST_NAME:-alertmanager}.${HOST_DOMAIN}`)`
- `traefik.http.services.alertmanager.loadbalancer.server.port=9093`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${ALERTMANAGER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `joyride.host.name=${ALERTMANAGER_HOST_NAME:-alertmanager}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable prometheus-alertmanager

# Configure environment variables (if needed)
make scaffold prometheus-alertmanager

# Start the service
make up
```
