# Garage

> S3-compatible distributed object storage (AGPL licensed MinIO alternative)

## Links
- [Docker Image](https://hub.docker.com/r/dxflrs/garage)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/garage.yml)

## Docker Images
- `dxflrs/garage:${GARAGE_DOCKER_TAG:-v2.1.0}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GARAGE_ADMIN_HOST` | garage | Garage admin host |
| `GARAGE_ADMIN_PORT` | 3903 | Service port number |
| `GARAGE_ADMIN_TOKEN` |  | Garage admin token |
| `GARAGE_BLOCK_SIZE` | 1048576 | Garage block size |
| `GARAGE_COMPRESSION_LEVEL` | 1 | Garage compression level |
| `GARAGE_CONTAINER_NAME` | garage | Container name |
| `GARAGE_DB_ENGINE` | lmdb | Garage db engine |
| `GARAGE_DOCKER_TAG` | v2.1.0 | Docker image tag/version |
| `GARAGE_METRICS_TOKEN` |  | Garage metrics token |
| `GARAGE_REPLICATION_FACTOR` | 1 | Garage replication factor |
| `GARAGE_RESTART` |  | Container restart policy |
| `GARAGE_RPC_SECRET` | CHANGE_ME_RUN_openssl_rand_hex_32 | Garage rpc secret |
| `GARAGE_S3_HOST` | s3 | Garage s3 host |
| `GARAGE_S3_PORT` | 3900 | Service port number |
| `GARAGE_S3_REGION` | garage | Garage s3 region |
| `GARAGE_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `GARAGE_WEB_PORT` | 3902 | Service port number |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/garage/garage.toml:/etc/garage.toml` - Volume mount
- `./etc/garage/meta:/var/lib/garage/meta` - Volume mount
- `./etc/garage/data:/var/lib/garage/data` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.garage-admin.entrypoints=websecure`
- `traefik.http.routers.garage-admin.rule=Host(`${GARAGE_ADMIN_HOST:-garage}.${HOST_DOMAIN}`)`
- `traefik.http.routers.garage-admin.service=garage-admin-backend`
- `traefik.http.routers.garage-admin.tls=true`
- `traefik.http.routers.garage-s3-buckets.entrypoints=websecure`
- `traefik.http.routers.garage-s3-buckets.rule=HostRegexp(`{subdomain:[a-z0-9-]+}.${GARAGE_S3_HOST:-s3}.${HOST_DOMAIN}`)`
- `traefik.http.routers.garage-s3-buckets.service=garage-s3-backend`
- `traefik.http.routers.garage-s3-buckets.tls=true`
- `traefik.http.routers.garage-s3.entrypoints=websecure`
- `traefik.http.routers.garage-s3.rule=Host(`${GARAGE_S3_HOST:-s3}.${HOST_DOMAIN}`)`
- `traefik.http.routers.garage-s3.service=garage-s3-backend`
- `traefik.http.routers.garage-s3.tls=true`
- `traefik.http.services.garage-admin-backend.loadbalancer.server.port=${GARAGE_ADMIN_PORT:-3903}`
- `traefik.http.services.garage-s3-backend.loadbalancer.server.port=${GARAGE_S3_PORT:-3900}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GARAGE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GARAGE_CONTAINER_NAME:-garage}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable garage

# Configure environment variables (if needed)
make scaffold garage

# Start the service
make up
```
