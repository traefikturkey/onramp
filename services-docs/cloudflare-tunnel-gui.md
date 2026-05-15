# Cloudflare Tunnel Gui

> Provides a graphical interface for cloudflare tunnel

## Links
- [Official Repository](https://github.com/cloudflare/cloudflared)
- [Docker Image](https://hub.docker.com/r/cloudflare/cloudflared)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cloudflare-tunnel-gui.yml)

## Docker Images
- `cloudflare/cloudflared:${CLOUDFLARE_TUNNEL_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUDFLARED_TOKEN` |  | Cloudflared token |
| `CLOUDFLARE_TUNNEL_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `CLOUDFLARE_TUNNEL_CONTAINER_NAME` |  | Container name |
| `CLOUDFLARE_TUNNEL_DOCKER_TAG` |  | Docker image tag/version |
| `CLOUDFLARE_TUNNEL_RESTART` |  | Container restart policy |
| `CLOUDFLARE_TUNNEL_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `CLOUDFLARE_TUNNEL_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/cloudflared:/cloudflared` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CLOUDFLARE_TUNNEL_TRAEFIK_ENABLED:-false}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CLOUDFLARE_TUNNEL_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${CLOUDFLARE_TUNNEL_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable cloudflare-tunnel-gui

# Configure environment variables (if needed)
make scaffold cloudflare-tunnel-gui

# Start the service
make up
```
