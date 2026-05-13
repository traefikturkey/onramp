# Prometheus Loki

> Horizontally scalable, highly available log aggregation system

## Links
- [Official Repository](https://github.com/gliderlabs/logspout)
- [Official Documentation](https://grafana.com/docs/loki/latest/clients/promtail/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prometheus-loki.yml)

## Docker Images
- `grafana/loki:${LOKI_DOCKER_TAG:-latest}`
- `gliderlabs/logspout:${LOGSPOUT_DOCKER_TAG:-latest}`
- `grafana/promtail:${PROMTAIL_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOGSPOUT_DOCKER_TAG` |  | Docker image tag/version |
| `LOKI_CONTAINER_NAME` |  | Container name |
| `LOKI_DOCKER_TAG` |  | Docker image tag/version |
| `LOKI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PROMTAIL_DOCKER_TAG` |  | Docker image tag/version |

## Configuration

### Ports
- `3100:3100`

### Volumes
- `./etc/loki:/etc/loki` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `/var/log:/var/log` - Volume mount
- `./etc/promtail:/etc/promtail` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${LOKI_WATCHTOWER_ENABLED:-true}`

### Dependencies
This service depends on:
- `promtail`

## Quick Start

```bash
# Enable the service
make enable prometheus-loki

# Configure environment variables (if needed)
make scaffold prometheus-loki

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires promtail to be running
