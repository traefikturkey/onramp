# Nginx

> High-performance static file server and reverse proxy

## Links
- [Docker Image](https://hub.docker.com/_/nginx)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nginx.yml)

## Docker Images
- `nginx:${NGINX_DOCKER_TAG:-alpine}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NGINX_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `NGINX_CONTAINER_NAME` |  | Container name |
| `NGINX_DOCKER_TAG` |  | Docker image tag/version |
| `NGINX_HOST_NAME` |  | Nginx host name |
| `NGINX_MEM_LIMIT` |  | Nginx mem limit |
| `NGINX_RESTART` |  | Container restart policy |
| `NGINX_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `NGINX_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./media/nginx:/usr/share/nginx/html` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${NGINX_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.nginx.entrypoints=websecure`
- `traefik.http.routers.nginx.rule=Host(`${NGINX_HOST_NAME:-nginx}.${HOST_DOMAIN}`)`
- `traefik.http.services.nginx.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NGINX_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${NGINX_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${NGINX_HOST_NAME:-nginx}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable nginx

# Configure environment variables (if needed)
make scaffold nginx

# Start the service
make up
```
