# Cert Dumper

> Extracts ssl certificate information from traefik acme.json file

## Links
- [Official Repository](https://github.com/kereis/traefik-certs-dumper)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cert-dumper.yml)

## Docker Images
- `ghcr.io/kereis/traefik-certs-dumper:${TRAEFIK_CERT_DUMPER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TRAEFIK_CERT_DUMPER_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `TRAEFIK_CERT_DUMPER_CONTAINER_NAME` |  | Container name |
| `TRAEFIK_CERT_DUMPER_DOCKER_TAG` |  | Docker image tag/version |
| `TRAEFIK_CERT_DUMPER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/traefik/letsencrypt:/data` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${TRAEFIK_CERT_DUMPER_WATCHTOWER_ENABLED:-false}`

**Other Labels:**
- `autoheal=${TRAEFIK_CERT_DUMPER_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable cert-dumper

# Configure environment variables (if needed)
make scaffold cert-dumper

# Start the service
make up
```
