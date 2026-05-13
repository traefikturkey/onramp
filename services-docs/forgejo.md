# Forgejo

> Self-hosted lightweight software forge, a fork of Gitea

## Links
- [Official Documentation](https://forgejo.org/docs/latest/admin/installation/docker/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/forgejo.yml)

## Docker Images
- `codeberg.org/forgejo/forgejo:${FORGEJO_DOCKER_TAG:-13}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FORGEJO_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `FORGEJO_CONTAINER_NAME` | forgejo | Container name |
| `FORGEJO_DOCKER_TAG` | 13 | Docker image tag/version |
| `FORGEJO_RESTART` | unless-stopped | Container restart policy |
| `FORGEJO_SSH_PORT` | 222 | Service port number |
| `FORGEJO_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `FORGEJO_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |

## Configuration

### Ports
- `${FORGEJO_SSH_PORT:-222}:22`

### Volumes
- `./etc/forgejo:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${FORGEJO_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.forgejo.entrypoints=websecure`
- `traefik.http.routers.forgejo.rule=Host(`${FORGEJO_CONTAINER_NAME:-forgejo}.${HOST_DOMAIN}`)`
- `traefik.http.services.forgejo.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FORGEJO_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${FORGEJO_AUTOHEAL:-true}`
- `joyride.host.name=${FORGEJO_CONTAINER_NAME:-forgejo}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable forgejo

# Configure environment variables (if needed)
make scaffold forgejo

# Start the service
make up
```
