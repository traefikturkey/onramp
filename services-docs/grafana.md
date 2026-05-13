# Grafana

> Platform for monitoring and observability

## Links
- [Official Repository](https://github.com/prometheus/prometheus)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/grafana.yml)

## Docker Images
- `grafana/grafana:${GRAFANA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GRAFANA_CONTAINER_NAME` |  | Container name |
| `GRAFANA_DOCKER_TAG` |  | Docker image tag/version |
| `GRAFANA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PUID` |  | User ID for file permissions |

## Configuration

### Volumes
- `./etc/grafana:/var/lib/grafana` - Volume mount
- `./etc/grafana/provisioning:/etc/grafana/provisioning` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`
- `default`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=true`
- `traefik.http.routers.grafana.entrypoints=websecure`
- `traefik.http.routers.grafana.rule=Host(`${GRAFANA_CONTAINER_NAME:-grafana}.${HOST_DOMAIN}`)`
- `traefik.http.services.grafana.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GRAFANA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `joyride.host.name=${GRAFANA_CONTAINER_NAME:-grafana}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable grafana

# Configure environment variables (if needed)
make scaffold grafana

# Start the service
make up
```
