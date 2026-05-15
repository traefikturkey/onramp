# Dockerizalo

> Docker build and deployment platform

## Links
- [Official Repository](https://github.com/undernightcore/dockerizalo)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/dockerizalo.yml)

## Docker Images
- `ghcr.io/undernightcore/dockerizalo-proxy:latest`
- `ghcr.io/undernightcore/dockerizalo-ui:latest`
- `ghcr.io/undernightcore/dockerizalo:latest`
- `postgres`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DOCKERIZALO_API_CONTAINER_NAME` |  | Container name |
| `DOCKERIZALO_DB_CONTAINER_NAME` |  | Container name |
| `DOCKERIZALO_PROXY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `DOCKERIZALO_PROXY_CONTAINER_NAME` |  | Container name |
| `DOCKERIZALO_PROXY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `DOCKERIZALO_PROXY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `DOCKERIZALO_UI_CONTAINER_NAME` |  | Container name |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Volumes
- `./etc/dockerizalo/api:/data/dockerizalo` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `./etc/dockerizalo/db:/var/lib/postgresql/data` - Volume mount

### Networks
- `dockerizalo-db`
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=false`
- `traefik.http.routers.dockerizalo.entrypoints=websecure`
- `traefik.http.routers.dockerizalo.rule=Host(`${DOCKERIZALO_PROXY_CONTAINER_NAME:-dockerizalo}.${HOST_DOMAIN}`)`
- `traefik.http.services.dockerizalo.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${DOCKERIZALO_PROXY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${DOCKERIZALO_PROXY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${DOCKERIZALO_PROXY_CONTAINER_NAME:-dockerizalo}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `api`
- `ui`

## Quick Start

```bash
# Enable the service
make enable dockerizalo

# Configure environment variables (if needed)
make scaffold dockerizalo

# Start the service
make up
```

## Notes
- This service consists of 4 containers working together
- Requires api, ui to be running
