# Nebula Sync

> Synchronize Pi-hole v6.x configuration to replicas.

## Links
- [Official Repository](https://github.com/lovelaze/nebula-sync)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nebula-sync.yml)

## Docker Images
- `ghcr.io/lovelaze/nebula-sync:${NEBULA_SYNC_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `NEBULA_SYNC_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `NEBULA_SYNC_CLIENT_SKIP_TLS_VERIFICATION` |  | Nebula sync client skip tls verification |
| `NEBULA_SYNC_CONTAINER_NAME` |  | Container name |
| `NEBULA_SYNC_CRON` |  | Nebula sync cron |
| `NEBULA_SYNC_DOCKER_TAG` |  | Docker image tag/version |
| `NEBULA_SYNC_FULL_SYNC` |  | Nebula sync full sync |
| `NEBULA_SYNC_MEM_LIMIT` |  | Nebula sync mem limit |
| `NEBULA_SYNC_PRIMARY` |  | Nebula sync primary |
| `NEBULA_SYNC_REPLICAS` |  | Nebula sync replicas |
| `NEBULA_SYNC_RESTART` |  | Container restart policy |
| `NEBULA_SYNC_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/nebula-sync:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NEBULA_SYNC_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${NEBULA_SYNC_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable nebula-sync

# Configure environment variables (if needed)
make scaffold nebula-sync

# Start the service
make up
```
