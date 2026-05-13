# Cloudbeaver

> CloudBeaver is a lightweight web application designed for efficient and secure data management. It supports a wide range of databases, including SQL, NoSQL, and cloud databases, all accessible through a web browser.

## Links
- [Official Documentation](https://dbeaver.com/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cloudbeaver.yml)

## Docker Images
- `dbeaver/cloudbeaver:${CLOUDBEAVER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLOUDBEAVER_ADMIN_NAME` |  | Cloudbeaver admin name |
| `CLOUDBEAVER_ADMIN_PASSWORD` |  | Service password |
| `CLOUDBEAVER_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `CLOUDBEAVER_CONTAINER_NAME` |  | Container name |
| `CLOUDBEAVER_DOCKER_TAG` |  | Docker image tag/version |
| `CLOUDBEAVER_HOST_NAME` |  | Cloudbeaver host name |
| `CLOUDBEAVER_RESTART` |  | Container restart policy |
| `CLOUDBEAVER_SERVER_NAME` |  | Cloudbeaver server name |
| `CLOUDBEAVER_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `CLOUDBEAVER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/cloudbeaver/workspace:/opt/cloudbeaver/workspace` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CLOUDBEAVER_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.cloudbeaver.entrypoints=websecure`
- `traefik.http.routers.cloudbeaver.rule=Host(`${CLOUDBEAVER_HOST_NAME:-cloudbeaver}.${HOST_DOMAIN}`)`
- `traefik.http.services.cloudbeaver.loadbalancer.server.port=8978`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CLOUDBEAVER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${CLOUDBEAVER_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${CLOUDBEAVER_HOST_NAME:-cloudbeaver}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable cloudbeaver

# Configure environment variables (if needed)
make scaffold cloudbeaver

# Start the service
make up
```
