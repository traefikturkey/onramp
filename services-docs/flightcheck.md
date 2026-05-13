# Flightcheck

> Google Flights MCP server (fli) - search flights via MCP protocol

## Links
- [Official Repository](https://github.com/crack-kitty/fli)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/flightcheck.yml)

## Docker Images
- `postgres:16-alpine`
- `ghcr.io/crack-kitty/fli:${FLIGHTCHECK_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FLIGHTCHECK_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `FLIGHTCHECK_CONTAINER_NAME` |  | Container name |
| `FLIGHTCHECK_DOCKER_TAG` |  | Docker image tag/version |
| `FLIGHTCHECK_HOST_NAME` |  | Flightcheck host name |
| `FLIGHTCHECK_MEM_LIMIT` |  | Flightcheck mem limit |
| `FLIGHTCHECK_POSTGRES_PASSWORD` |  | Service password |
| `FLIGHTCHECK_RESTART` |  | Container restart policy |
| `FLIGHTCHECK_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `FLIGHTCHECK_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `8000:8000`

### Volumes
- `flightcheck-pgdata:/var/lib/postgresql/data` - Data storage
- `./etc/flightcheck/initdb:/docker-entrypoint-initdb.d` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${FLIGHTCHECK_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.flightcheck.entrypoints=websecure`
- `traefik.http.routers.flightcheck.rule=Host(`${FLIGHTCHECK_HOST_NAME:-flightcheck}.${HOST_DOMAIN}`)`
- `traefik.http.services.flightcheck.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FLIGHTCHECK_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${FLIGHTCHECK_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${FLIGHTCHECK_HOST_NAME:-flightcheck}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable flightcheck

# Configure environment variables (if needed)
make scaffold flightcheck

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
