# Prometheus All

> Collection of prometheus exporters and dashboards

## Links
- [Official Repository](https://github.com/prometheus/prometheus)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prometheus-all.yml)

## Docker Images
- `prom/prometheus:${PROMETHEUS_DOCKER_TAG:-latest}`
- `ghcr.io/ilude/prometheus-pve-exporter`
- `prom/blackbox-exporter:latest`
- `prom/alertmanager:latest`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PROMETHEUS_DOCKER_TAG` |  | Docker image tag/version |
| `PROMETHEUS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/prometheus/conf:/etc/prometheus/conf` - Volume mount
- `prometheus:/prometheus` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/prometheus/conf:/etc/alertmanager` - Volume mount
- `prometheus:/alertmanager` - Volume mount

### Networks
- `traefik`
- `default`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=true`
- `traefik.http.routers.alertmanager.entrypoints=websecure`
- `traefik.http.routers.alertmanager.rule=Host(`alertmanager.${HOST_DOMAIN}`)`
- `traefik.http.routers.alertmanager.tls=true`
- `traefik.http.routers.alertmanager.tls.certresolver=letsencrypt`
- `traefik.http.routers.blackbox.entrypoints=websecure`
- `traefik.http.routers.blackbox.rule=Host(`blackbox.${HOST_DOMAIN}`)`
- `traefik.http.routers.blackbox.tls=true`
- `traefik.http.routers.blackbox.tls.certresolver=letsencrypt`
- `traefik.http.routers.prometheus.entrypoints=websecure`
- `traefik.http.routers.prometheus.rule=Host(`prometheus.${HOST_DOMAIN}`)`
- `traefik.http.services.alertmanager.loadbalancer.server.port=9093`
- `traefik.http.services.alertmanager.loadbalancer.server.scheme=http`
- `traefik.http.services.blackbox.loadbalancer.server.port=9115`
- `traefik.http.services.blackbox.loadbalancer.server.scheme=http`
- `traefik.http.services.prometheus.loadbalancer.server.port=9090`
- `traefik.http.services.prometheus.loadbalancer.server.scheme=http`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${PROMETHEUS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `joyride.host.name=alertmanager.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable prometheus-all

# Configure environment variables (if needed)
make scaffold prometheus-all

# Start the service
make up
```

## Notes
- This service consists of 4 containers working together
