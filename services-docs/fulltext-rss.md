# Fulltext Rss

> Generates full-text rss feeds from partial feeds

## Links
- [Official Documentation](https://www.youtube.com/watch?v=nxV0CPNeFxY)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/fulltext-rss.yml)

## Docker Images
- `heussd/fivefilters-full-text-rss:${FULLTEXT_RSS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FULLTEXT_RSS_CONTAINER_NAME` |  | Container name |
| `FULLTEXT_RSS_DOCKER_TAG` |  | Docker image tag/version |
| `FULLTEXT_RSS_RESTART` |  | Container restart policy |
| `FULLTEXT_RSS_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/fulltext-rss:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.fulltext-rss.entrypoints=websecure`
- `traefik.http.routers.fulltext-rss.rule=Host(`${FULLTEXT_RSS_CONTAINER_NAME:-fulltext-rss}.${HOST_DOMAIN}`)`
- `traefik.http.services.fulltext-rss.loadbalancer.server.port=8096`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FULLTEXT_RSS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FULLTEXT_RSS_CONTAINER_NAME:-fulltext-rss}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable fulltext-rss

# Configure environment variables (if needed)
make scaffold fulltext-rss

# Start the service
make up
```
