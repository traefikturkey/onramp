# Prometheus

> Monitoring and alerting toolkit

## Links
- [Official Repository](https://github.com/prometheus/prometheus)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prometheus.yml)

## Docker Images
- `prom/prometheus:${PROMETHEUS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PROMETHEUS_CONTAINER_NAME` | prometheus | Container name |
| `PROMETHEUS_DOCKER_TAG` | latest | Docker image tag/version |
| `PROMETHEUS_HOST_NAME` |  | Prometheus host name |
| `PROMETHEUS_LOG_LEVEL` |  | Prometheus log level |
| `PROMETHEUS_RESTART` | unless-stopped | Container restart policy |
| `PROMETHEUS_RETENTION_SIZE` | 0 | Prometheus retention size |
| `PROMETHEUS_RETENTION_TIME` | 15d | Prometheus retention time |
| `PROMETHEUS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/prometheus/conf:/etc/prometheus/conf` - Volume mount
- `prometheus:/prometheus` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`
- `default`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=true`
- `traefik.http.routers.prometheus.entrypoints=websecure`
- `traefik.http.routers.prometheus.rule=Host(`${PROMETHEUS_HOST_NAME:-prometheus}.${HOST_DOMAIN}`)`
- `traefik.http.services.prometheus.loadbalancer.server.port=9090`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PROMETHEUS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${PROMETHEUS_HOST_NAME:-prometheus}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable prometheus

# Configure environment variables (if needed)
make scaffold prometheus

# Start the service
make up
```
