# Newsdash

> Self-hosted rss feed reader and dashboard

## Links
- [Official Repository](https://github.com/buzz/newsdash)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/newsdash.yml)

## Docker Images
- `newsdash/newsdash:${NEWSDASH_DOCKER_TAG:-latest}`
- `bitnami/redis`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NEWSDASH_DOCKER_RESTART_POLICY` |  | Container restart policy |
| `NEWSDASH_DOCKER_TAG` |  | Docker image tag/version |
| `NEWSDASH_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `REDIS_DOCKER_RESTART_POLICY` |  | Container restart policy |
| `REDIS_LOG_LEVEL` |  | Redis log level |

## Configuration

### Volumes
- `./etc/newsdash:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `redis:/bitnami` - Volume mount

### Networks
- `traefik`
- `default`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.newsdash.entrypoints=websecure`
- `traefik.http.routers.newsdash.rule=Host(`newsdash.${HOST_DOMAIN}`)`
- `traefik.http.services.newsdash.loadbalancer.server.port=3001`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NEWSDASH_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=newsdash.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable newsdash

# Configure environment variables (if needed)
make scaffold newsdash

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
