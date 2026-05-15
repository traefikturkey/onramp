# Kitchenowl

> Grocery list and recipe manager

## Links
- [Official Repository](https://github.com/TomBursch/kitchenowl)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/kitchenowl.yml)

## Docker Images
- `tombursch/kitchenowl-backend:latest`
- `tombursch/kitchenowl-web:latest`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KITCHENOWL_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `KITCHENOWL_CONTAINER_NAME` |  | Container name |
| `KITCHENOWL_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `KITCHENOWL_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/kitchenowl/app:/data` - Volume mount

### Networks
- `kitchenowl-db`
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${KITCHENOWL_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.kitchenowl.entrypoints=websecure`
- `traefik.http.routers.kitchenowl.rule=Host(`${KITCHENOWL_CONTAINER_NAME:-kitchenowl}.${HOST_DOMAIN}`)`
- `traefik.http.services.kitchenowl.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KITCHENOWL_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${KITCHENOWL_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${KITCHENOWL_CONTAINER_NAME:-kitchenowl}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `kitchenowl_app`

## Quick Start

```bash
# Enable the service
make enable kitchenowl

# Configure environment variables (if needed)
make scaffold kitchenowl

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires kitchenowl_app to be running
