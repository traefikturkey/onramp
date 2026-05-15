# Gitlab

> Self-hosted git repository management system

## Links
- [Official Documentation](https://docs.gitlab.com/ee/install/docker.html)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/gitlab.yml)

## Docker Images
- `gitlab/gitlab-ce:${GITLAB_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GITLAB_CONTAINER_NAME` |  | Container name |
| `GITLAB_DOCKER_TAG` |  | Docker image tag/version |
| `GITLAB_RESTART` |  | Container restart policy |
| `GITLAB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `222:22`

### Volumes
- `./etc/gitlab/config:/etc/config` - Configuration files
- `./etc/gitlab/data:/var/opt/gitlab` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.gitlab.entrypoints=websecure`
- `traefik.http.routers.gitlab.rule=Host(`${GITLAB_CONTAINER_NAME:-gitlab}.${HOST_DOMAIN}`)`
- `traefik.http.routers.gitlab.service=gitlab`
- `traefik.http.routers.gitlab.tls=true`
- `traefik.http.services.gitlab.loadbalancer.server.port=443`
- `traefik.http.services.gitlab.loadbalancer.server.scheme=https`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GITLAB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GITLAB_CONTAINER_NAME:-gitlab}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable gitlab

# Configure environment variables (if needed)
make scaffold gitlab

# Start the service
make up
```
