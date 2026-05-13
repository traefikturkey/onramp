# Prometheus Blackbox Exporter

> Tests endpoints over http, https, dns, and more

## Links
- [Official Repository](https://github.com/prometheus/blackbox_exporter)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prometheus-blackbox-exporter.yml)

## Docker Images
- `prom/blackbox-exporter:${BLACKBOX_EXPORTER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BLACKBOX_EXPORTER_DOCKER_TAG` |  | Docker image tag/version |
| `BLACKBOX_EXPORTER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Volumes
- `./etc/prometheus/conf:/etc/prometheus/conf` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.blackbox.entrypoints=websecure`
- `traefik.http.routers.blackbox.rule=Host(`blackbox.${HOST_DOMAIN}`)`
- `traefik.http.services.blackbox.loadbalancer.server.port=9115`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BLACKBOX_EXPORTER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=blackbox.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable prometheus-blackbox-exporter

# Configure environment variables (if needed)
make scaffold prometheus-blackbox-exporter

# Start the service
make up
```
