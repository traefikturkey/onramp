# Wordpress

> Popular content management system (cms)

## Links
- [Docker Image](https://hub.docker.com/_/wordpress)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/wordpress.yml)

## Docker Images
- `wordpress:${WORDPRESS_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `WORDPRESS_CONTAINER_NAME` | wordpress | Container name |
| `WORDPRESS_DATABASE_HOST` | mariadb | Wordpress database host |
| `WORDPRESS_DATABASE_NAME` | wordpress | Wordpress database name |
| `WORDPRESS_DATABASE_PASSWORD` | ${MARIADB_PASS} | Service password |
| `WORDPRESS_DATABASE_USER` | wordpress | Service username |
| `WORDPRESS_DOCKER_TAG` | latest | Docker image tag/version |
| `WORDPRESS_HOST_NAME` | wordpress | Wordpress host name |
| `WORDPRESS_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |

## Configuration

### Ports
- `8080:80`

### Volumes
- `./etc/wordpress:/var/www/html/` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.wordpress.entrypoints=websecure`
- `traefik.http.routers.wordpress.rule=Host(`${WORDPRESS_HOST_NAME:-wordpress}.${HOST_DOMAIN}`)`
- `traefik.http.services.wordpress.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${WORDPRESS_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${WORDPRESS_HOST_NAME:-wordpress}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### wordpress-upload

**Purpose**: Alternative configuration for this service

**Changes**:
- **Adds/modifies services**: `wordpress`

**Usage**:
```bash
make enable-override wordpress-upload
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/wordpress-upload.yml)

## Quick Start

```bash
# Enable the service
make enable wordpress

# Configure environment variables (if needed)
make scaffold wordpress

# Start the service
make up
```
