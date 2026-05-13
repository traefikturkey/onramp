# Nocodb

> Databases As Spreadsheets

## Links
- [Official Repository](https://github.com/nocodb/nocodb)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/nocodb.yml)

## Docker Images
- `nocodb/nocodb:${NOCODB_DOCKER_TAG:-latest}`
- `postgres:12.17-alpine`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `NOCODB_ATTACHMENT_EXPIRE_SECONDS` |  | Nocodb attachment expire seconds |
| `NOCODB_ATTACHMENT_FIELD_SIZE` |  | Nocodb attachment field size |
| `NOCODB_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `NOCODB_CONTAINER_NAME` |  | Container name |
| `NOCODB_DOCKER_TAG` |  | Docker image tag/version |
| `NOCODB_HOST_NAME` |  | Nocodb host name |
| `NOCODB_MAX_ATTACHMENTS_ALLOWED` |  | Nocodb max attachments allowed |
| `NOCODB_POSTGRES_DB` |  | PostgreSQL database name |
| `NOCODB_POSTGRES_DB_PW` |  | PostgreSQL database name |
| `NOCODB_POSTGRES_USER` |  | Service username |
| `NOCODB_RESTART` |  | Container restart policy |
| `NOCODB_SECURE_ATTACHMENTS` |  | Nocodb secure attachments |
| `NOCODB_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `NOCODB_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/nocodb/data:/usr/app/data` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/nocodb/postgresql:/var/lib/postgresql/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${NOCODB_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.nocodb.entrypoints=websecure`
- `traefik.http.routers.nocodb.rule=Host(`${NOCODB_HOST_NAME:-nocodb}.${HOST_DOMAIN}`)`
- `traefik.http.services.nocodb.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${NOCODB_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${NOCODB_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${NOCODB_HOST_NAME:-nocodb}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `nocodb_postgres`

## Quick Start

```bash
# Enable the service
make enable nocodb

# Configure environment variables (if needed)
make scaffold nocodb

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires nocodb_postgres to be running
