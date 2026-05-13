# Woodpecker

> CI/CD server and agent runner, a fork of Drone CI

## Links
- [Official Documentation](https://woodpecker-ci.org/docs/intro)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/woodpecker.yml)

## Docker Images
- `woodpeckerci/woodpecker-server:${WOODPECKER_DOCKER_TAG:-latest}`
- `woodpeckerci/woodpecker-agent:latest`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GITEA_CONTAINER_NAME` | gitea | Container name |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WOODPECKER_ADMIN` | admin | Woodpecker admin |
| `WOODPECKER_AGENT_SECRET` | changeme | Woodpecker agent secret |
| `WOODPECKER_CONTAINER_NAME` | woodpecker | Container name |
| `WOODPECKER_DOCKER_TAG` | latest | Docker image tag/version |
| `WOODPECKER_GITEA_CLIENT` | changeme | Woodpecker gitea client |
| `WOODPECKER_GITEA_SECRET` | changeme | Woodpecker gitea secret |
| `WOODPECKER_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/woodpecker:/var/lib/woodpecker` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`
- `default`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.woodpecker.entrypoints=websecure`
- `traefik.http.routers.woodpecker.rule=Host(`${WOODPECKER_CONTAINER_NAME:-woodpecker}.${HOST_DOMAIN}`)`
- `traefik.http.services.woodpecker.loadbalancer.server.port=8000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WOODPECKER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WOODPECKER_CONTAINER_NAME:-woodpecker}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `woodpecker`

## Quick Start

```bash
# Enable the service
make enable woodpecker

# Configure environment variables (if needed)
make scaffold woodpecker

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires woodpecker to be running
