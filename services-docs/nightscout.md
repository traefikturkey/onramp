# Nightscout

> web-based CGM (Continuous Glucose Monitor)

## Links
- [Official Repository](https://github.com/nightscout/cgm-remote-monitor)
- [Docker Image](https://hub.docker.com/r/nightscout/cgm-remote-monitor)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nightscout.yml)

## Docker Images
- `mongo:${NSMONGO_VERSION:-4.4}`
- `nightscout/cgm-remote-monitor:${NSWEB_VERSION:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NIGHTSCOUNT_CONTAINER_NAME` |  | Container name |
| `NIGHTSCOUNT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `NIGHTSCOUT_RESTART_POLICY` |  | Container restart policy |
| `NSMONGO_CONTAINER_NAME` |  | Container name |
| `NSMONGO_VERSION` |  | Nsmongo version |
| `NSWEB_CONTAINER_NAME` |  | Container name |
| `NSWEB_DEFAULT_ROLES` |  | Nsweb default roles |
| `NSWEB_ENABLED_SVCS` |  | Nsweb enabled svcs |
| `NSWEB_VERSION` |  | Nsweb version |
| `NS_API_SECRET` |  | Ns api secret |
| `NS_MONGO_DATA_DIR` |  | Data directory path |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${NS_MONGO_DATA_DIR:-./etc/ns-mongo-data}` - Data storage

### Networks
- `ns-db`
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.docker.network=traefik`
- `traefik.enable=true`
- `traefik.http.routers.nightscout.entrypoints=websecure`
- `traefik.http.routers.nightscout.rule=Host(`${NIGHTSCOUNT_CONTAINER_NAME:-nightscout}.${HOST_DOMAIN}`)`
- `traefik.http.services.nightscout.loadbalancer.server.port=1337`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NIGHTSCOUNT_WATCHTOWER_ENABLED:-false}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${NIGHTSCOUNT_CONTAINER_NAME:-nightscout}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `ns-mongo`

## Quick Start

```bash
# Enable the service
make enable nightscout

# Configure environment variables (if needed)
make scaffold nightscout

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires ns-mongo to be running
