# Prometheus Proxmox Exporter

> Collects metrics from proxmox virtual environment

## Links
- [Official Repository](https://github.com/prometheus-pve/prometheus-pve-exporter)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/prometheus-proxmox-exporter.yml)

## Docker Images
- `ghcr.io/ilude/prometheus-pve-exporter:${PROXMOX_EXPORTER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PROXMOX_EXPORTER_DOCKER_TAG` |  | Docker image tag/version |

## Configuration

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

## Quick Start

```bash
# Enable the service
make enable prometheus-proxmox-exporter

# Configure environment variables (if needed)
make scaffold prometheus-proxmox-exporter

# Start the service
make up
```
