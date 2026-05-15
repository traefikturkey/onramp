# Prometheus Node Exporter

> Exposes hardware and os metrics to prometheus

## Links
- [Official Repository](https://github.com/prometheus/node_exporter)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prometheus-node-exporter.yml)

## Docker Images
- `prom/node-exporter:${NODE_EXPORTER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NODE_EXPORTER_DOCKER_TAG` |  | Docker image tag/version |

## Configuration

### Volumes
- `/proc:/host/proc` - Volume mount
- `/sys:/host/sys` - Volume mount
- `/:/rootfs` - Volume mount

## Quick Start

```bash
# Enable the service
make enable prometheus-node-exporter

# Configure environment variables (if needed)
make scaffold prometheus-node-exporter

# Start the service
make up
```
