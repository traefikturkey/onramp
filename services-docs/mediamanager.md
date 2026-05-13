# Mediamanager

> MediaManager is modern software to manage your TV and movie library

## Links
- [Official Repository](https://github.com/maxdorninger/MediaManager)
- [Official Documentation](https://maxdorninger.github.io/MediaManager/introduction.html)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mediamanager.yml)

## Docker Images
- `postgres:latest`
- `ghcr.io/maxdorninger/mediamanager/backend:${MEDIAMANAGERBACKEND_DOCKER_TAG:-latest}`
- `ghcr.io/maxdorninger/mediamanager/frontend:${MEDIAMANAGERFRONTEND_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MEDIAMANAGERBACKEND_DOCKER_TAG` |  | Docker image tag/version |
| `MEDIAMANAGERFRONTEND_DOCKER_TAG` |  | Docker image tag/version |
| `MEDIAMANAGERFRONT_CONTAINER_NAME` |  | Container name |
| `MEDIAMANAGER_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `MEDIAMANAGER_CONTAINER_NAME` |  | Container name |
| `MEDIAMANAGER_DB_NAME` |  | Mediamanager db name |
| `MEDIAMANAGER_HOST_NAME` |  | Mediamanager host name |
| `MEDIAMANAGER_MEM_LIMIT` |  | Mediamanager mem limit |
| `MEDIAMANAGER_RESTART` |  | Container restart policy |
| `MEDIAMANAGER_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `MEDIAMANAGER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `MM_ADMIN_EMAIL` |  | Mm admin email |
| `MM_AUTH_EMAIL_PASSWORD_RESETS` |  | Service password |
| `MM_AUTH_SESSION_LIFETIME` |  | Mm auth session lifetime |
| `MM_EMAIL_FROM_EMAIL` |  | Mm email from email |
| `MM_EMAIL_SMTP_HOST` |  | Mm email smtp host |
| `MM_EMAIL_SMTP_PASSWORD` |  | Service password |
| `MM_EMAIL_SMTP_PORT` |  | Service port number |
| `MM_EMAIL_USE_TLS` |  | Mm email use tls |
| `MM_JACKETT_API_KEY` |  | Mm jackett api key |
| `MM_JACKETT_ENABLED` |  | Mm jackett enabled |
| `MM_OPENID_CLIENT_ID` |  | Mm openid client id |
| `MM_OPENID_CLIENT_SECRET` |  | Mm openid client secret |
| `MM_OPENID_CONFIGURATION_ENDPOINT` |  | Mm openid configuration endpoint |
| `MM_OPENID_ENABLED` |  | Mm openid enabled |
| `MM_OPENID_NAME` |  | Mm openid name |
| `MM_POSTGRES_DB` |  | PostgreSQL database name |
| `MM_POSTGRES_PASSWORD` |  | Service password |
| `MM_POSTGRES_USER` |  | Service username |
| `MM_PROWLARR_API_KEY` |  | Mm prowlarr api key |
| `MM_PROWLARR_ENABLED` |  | Mm prowlarr enabled |
| `MM_TOKEN` |  | Mm token |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/mediamanager/db:/var/lib/postgresql/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/mediamanager/backend:/data` - Volume mount

### Networks
- `mm-internal`
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${MEDIAMANAGER_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.mediamanager.entrypoints=websecure`
- `traefik.http.routers.mediamanager.rule=Host(`${MEDIAMANAGER_HOST_NAME:-mediamanager}.${HOST_DOMAIN}`)`
- `traefik.http.services.mediamanager.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MEDIAMANAGER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${MEDIAMANAGER_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${MEDIAMANAGER_HOST_NAME:-mediamanager}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `mediamanager-backend`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### mediamanager-postgres

**Purpose**: Override to use dedicated PostgreSQL database for mediamanager

**Changes**:
- **Adds/modifies services**: `mediamanager-backend`, `mediamanager-frontend`, `mediamanager-db`
- **Adds/modifies environment variables**: `DB_HOST`, `DB_USER`, `DB_PASSWORD`, `DB_DBNAME`, `POSTGRES_USER`, `POSTGRES_DB`, `POSTGRES_PASSWORD`

**Usage**:
```bash
make enable-override mediamanager-postgres
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/mediamanager-postgres.yml)

## Quick Start

```bash
# Enable the service
make enable mediamanager

# Configure environment variables (if needed)
make scaffold mediamanager

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
- Requires mediamanager-backend to be running
