# Minio

> High-performance object storage server

## Links
- [Official Repository](https://github.com/minio/minio)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/minio.yml)

## Docker Images
- `minio/minio:${MINIO_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MINIO_ADMIN_PASSWORD` | changeme | Service password |
| `MINIO_ADMIN_USER` | admin | Service username |
| `MINIO_API_HOST` | minio-api | Minio api host |
| `MINIO_API_PORT` | 9000 | Service port number |
| `MINIO_CONTAINER_NAME` | minio | Container name |
| `MINIO_DASHBOARD_HOST` | minio | Minio dashboard host |
| `MINIO_DASHBOARD_PORT` | 9001 | Service port number |
| `MINIO_DOCKER_TAG` | latest | Docker image tag/version |
| `MINIO_RESTART` | unless-stopped | Container restart policy |
| `MINIO_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/minio/data:/data` - Data storage
- `./etc/minio/config:/root/.minio` - Configuration files

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.middlewares.gzip-compress.compress=true`
- `traefik.http.middlewares.redirect-to-https.redirectscheme.permanent=true`
- `traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https`
- `traefik.http.routers.minio-admin-http.entrypoints=web`
- `traefik.http.routers.minio-admin-http.middlewares=redirect-to-https@docker`
- `traefik.http.routers.minio-admin-http.rule=Host(`${MINIO_DASHBOARD_HOST}.${HOST_DOMAIN}`)`
- `traefik.http.routers.minio-admin-http.service=noop@internal`
- `traefik.http.routers.minio-admin-https.entrypoints=websecure`
- `traefik.http.routers.minio-admin-https.middlewares=gzip-compress@docker`
- `traefik.http.routers.minio-admin-https.rule=Host(`${MINIO_DASHBOARD_HOST}.${HOST_DOMAIN}`)`
- `traefik.http.routers.minio-admin-https.service=minio-admin-backend`
- `traefik.http.routers.minio-admin-https.tls=true`
- `traefik.http.routers.minio-http.entrypoints=web`
- `traefik.http.routers.minio-http.middlewares=redirect-to-https@docker`
- `traefik.http.routers.minio-http.rule=Host(`${MINIO_API_HOST}.${HOST_DOMAIN}`)`
- `traefik.http.routers.minio-http.service=noop@internal`
- `traefik.http.routers.minio-https.entrypoints=websecure`
- `traefik.http.routers.minio-https.middlewares=gzip-compress@docker`
- `traefik.http.routers.minio-https.rule=Host(`${MINIO_API_HOST}.${HOST_DOMAIN}`)`
- `traefik.http.routers.minio-https.service=minio-backend`
- `traefik.http.routers.minio-https.tls=true`
- `traefik.http.services.minio-admin-backend.loadbalancer.server.port=${MINIO_DASHBOARD_PORT}`
- `traefik.http.services.minio-admin-backend.loadbalancer.server.scheme=http`
- `traefik.http.services.minio-backend.loadbalancer.server.port=${MINIO_API_PORT}`
- `traefik.http.services.minio-backend.loadbalancer.server.scheme=http`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MINIO_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MINIO_CONTAINER_NAME:-minio}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### minio-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `minio-nfs-root`
- **Adds/modifies services**: `minio`

**Usage**:
```bash
make enable-override minio-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/minio-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable minio

# Configure environment variables (if needed)
make scaffold minio

# Start the service
make up
```
