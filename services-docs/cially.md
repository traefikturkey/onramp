# Cially

> Cially is a powerful, open-source dashboard designed to provide in-depth insights, real-time analytics, and detailed statistics for your Discord server.

## Links
- [Official Repository](https://github.com/skellgreco/cially)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cially.yml)

## Docker Images
- `ghcr.io/skellgreco/cially-bot:${CIALLY_DOCKER_TAG:-latest}`
- `ghcr.io/skellgreco/cially-web:latest`
- `ghcr.io/keksiqc/pocketbase:0.26.6`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CIALLY_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `CIALLY_BOT_CLIENT_ID` |  | Cially bot client id |
| `CIALLY_BOT_DEBUGGING` |  | Cially bot debugging |
| `CIALLY_BOT_TOKEN` |  | Cially bot token |
| `CIALLY_CONTAINER_NAME` |  | Container name |
| `CIALLY_DOCKER_TAG` |  | Docker image tag/version |
| `CIALLY_HOST_NAME` |  | Cially host name |
| `CIALLY_MEM_LIMIT` |  | Cially mem limit |
| `CIALLY_POCKETBASE_HOST_NAME` |  | Cially pocketbase host name |
| `CIALLY_RESTART` |  | Container restart policy |
| `CIALLY_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `CIALLY_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/cially/config:/config` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/cially/pocketbase-data:/pb/pb_data` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CIALLY_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.cially-pb.entrypoints=websecure`
- `traefik.http.routers.cially-pb.rule=Host(`${CIALLY_POCKETBASE_HOST_NAME:-cially-pb}.${HOST_DOMAIN}`)`
- `traefik.http.routers.cially.entrypoints=websecure`
- `traefik.http.routers.cially.rule=Host(`${CIALLY_HOST_NAME:-cially}.${HOST_DOMAIN}`)`
- `traefik.http.services.cially-pb.loadbalancer.server.port=8090`
- `traefik.http.services.cially.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CIALLY_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${CIALLY_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${CIALLY_POCKETBASE_HOST_NAME:-cially-pb}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `pocketbase`
- `cially-web`
- `pocketbase`

## Quick Start

```bash
# Enable the service
make enable cially

# Configure environment variables (if needed)
make scaffold cially

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires pocketbase, cially-web, pocketbase to be running
