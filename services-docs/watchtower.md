# Watchtower

> Automatically updates docker containers

## Links
- [Official Repository](https://github.com/containrrr/watchtower)
- [Official Documentation](https://containrrr.dev/watchtower/notifications/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/watchtower.yml)

## Docker Images
- `${WATCHTOWER_IMAGE:-ghcr.io/containrrr/watchtower}:${WATCHTOWER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |
| `WATCHTOWER_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `WATCHTOWER_CLEANUP` | false | Watchtower cleanup |
| `WATCHTOWER_CONTAINER_NAME` | watchtower | Container name |
| `WATCHTOWER_DOCKER_API_VERSION` | 1.44 | Watchtower docker api version |
| `WATCHTOWER_DOCKER_TAG` | latest | Docker image tag/version |
| `WATCHTOWER_HTTP_API_METRICS` | false | Watchtower http api metrics |
| `WATCHTOWER_HTTP_API_TOKEN` | watchtower_secret_token | Watchtower http api token |
| `WATCHTOWER_IMAGE` | ghcr.io/containrrr/watchtower | Watchtower image |
| `WATCHTOWER_MEM_LIMIT` | 100m | Watchtower mem limit |
| `WATCHTOWER_MONITOR_ONLY` | false | Watchtower monitor only |
| `WATCHTOWER_NOTIFICATIONS` | shoutrrr | Watchtower notifications |
| `WATCHTOWER_NOTIFICATIONS_HOSTNAME` | ${HOST_NAME | Watchtower notifications hostname |
| `WATCHTOWER_NOTIFICATION_TITLE_TAG` | watchtower | Watchtower notification title tag |
| `WATCHTOWER_NOTIFICATION_URL` | ${WATCHTOWER_NOTIFICATION_URL:-} | Watchtower notification url |
| `WATCHTOWER_RESTART` | unless-stopped | Container restart policy |
| `WATCHTOWER_SCHEDULE` | 0 0 4 * * * | Watchtower schedule |
| `WATCHTOWER_TRAEFIK_ENABLE` | false | Enable Traefik reverse proxy |

## Configuration

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${WATCHTOWER_TRAEFIK_ENABLE:-false}`

**Other Labels:**
- `autoheal=${WATCHTOWER_AUTOHEAL:-true}`

## Quick Start

```bash
# Enable the service
make enable watchtower

# Configure environment variables (if needed)
make scaffold watchtower

# Start the service
make up
```
