# Cloudflare Ddns

> Updates dns records on cloudflare dynamically

## Links
- [Official Repository](https://github.com/favonia/cloudflare-ddns)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cloudflare-ddns.yml)

## Docker Images
- `ghcr.io/favonia/cloudflare-ddns:${CLOUDFLARE_DDNS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CF_DNS_API_TOKEN` | changeme | Cf dns api token |
| `CLOUDFLARE_DDNS_CONTAINER_NAME` | cloudflare-ddns | Container name |
| `CLOUDFLARE_DDNS_DOCKER_TAG` | latest | Docker image tag/version |
| `CLOUDFLARE_DDNS_HOSTNAME` | ddns | Cloudflare ddns hostname |
| `CLOUDFLARE_DDNS_PROXIED` | false | Cloudflare ddns proxied |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

## Quick Start

```bash
# Enable the service
make enable cloudflare-ddns

# Configure environment variables (if needed)
make scaffold cloudflare-ddns

# Start the service
make up
```
