# Cloudflare Tunnel

> Creates secure tunnels to expose local services

## Links
- [Official Repository](https://github.com/cloudflare/cloudflared/issues/163)
- [Docker Image](https://hub.docker.com/r/cloudflare/cloudflared)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cloudflare-tunnel.yml)

## Docker Images
- `privatebin/chown:1.34.1-musl-1.2.2-r3`
- `cloudflare/cloudflared:${CLOUDFLARE_TUNNEL_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUDFLARE_TUNNEL_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `CLOUDFLARE_TUNNEL_CONTAINER_NAME` |  | Container name |
| `CLOUDFLARE_TUNNEL_DOCKER_TAG` |  | Docker image tag/version |
| `CLOUDFLARE_TUNNEL_NAME` |  | Cloudflare tunnel name |
| `CLOUDFLARE_TUNNEL_RESTART` |  | Container restart policy |
| `CLOUDFLARE_TUNNEL_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `CLOUDFLARE_TUNNEL_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `HOST_NAME` |  | Host name |

## Configuration

### Volumes
- `./etc/cloudflare-tunnel:/mnt` - Volume mount
- `./etc/cloudflare-tunnel:/home/nonroot/.cloudflared/` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=${CLOUDFLARE_TUNNEL_TRAEFIK_ENABLED:-false}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CLOUDFLARE_TUNNEL_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${CLOUDFLARE_TUNNEL_AUTOHEAL_ENABLED:-true}`

### Dependencies
This service depends on:
- `cloudflared_chown`

## Quick Start

```bash
# Enable the service
make enable cloudflare-tunnel

# Configure environment variables (if needed)
make scaffold cloudflare-tunnel

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires cloudflared_chown to be running
