# Gitea

> Lightweight git service similar to github

## Links
- [Official Repository](https://github.com/go-gitea/gitea)
- [Official Documentation](https://docs.gitea.io/en-us/install-with-docker/#environments-variables)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/gitea.yml)

## Docker Images
- `gitea/gitea:${GITEA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GITEA_CONTAINER_NAME` |  | Container name |
| `GITEA_DOCKER_TAG` |  | Docker image tag/version |
| `GITEA_REPOSITORY_NAME` |  | Gitea repository name |
| `GITEA_SSH_PORT` |  | Service port number |
| `GITEA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |

## Configuration

### Ports
- `2222:22`

### Volumes
- `./etc/gitea:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.gitea.entrypoints=websecure`
- `traefik.http.routers.gitea.rule=Host(`${GITEA_CONTAINER_NAME:-gitea}.${HOST_DOMAIN}`)`
- `traefik.http.services.gitea.loadbalancer.server.port=4000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GITEA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GITEA_CONTAINER_NAME:-gitea}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable gitea

# Configure environment variables (if needed)
make scaffold gitea

# Start the service
make up
```
