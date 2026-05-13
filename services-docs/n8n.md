# N8N

> workflow automation platform with native AI capabilities

## Links
- [Official Repository](https://github.com/n8n-io/n8n)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/n8n.yml)

## Docker Images
- `n8nio/n8n:${N8N_DOCKER_TAG:-latest}`
- `postgres:16`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DB_TYPE` |  | Db type |
| `HOST_DOMAIN` |  | Host domain for service access |
| `N8N_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `N8N_BASIC_AUTH_PASSWORD` | password | Service password |
| `N8N_BASIC_AUTH_USER` | user | Service username |
| `N8N_CONTAINER_NAME` | n8n | Container name |
| `N8N_DATA_PATH` |  | N8n data path |
| `N8N_DOCKER_TAG` | latest | Docker image tag/version |
| `N8N_HOST_NAME` | n8n | N8n host name |
| `N8N_MEM_LIMIT` | 200g | N8n mem limit |
| `N8N_NODE_ENV` |  | N8n node env |
| `N8N_PORT` |  | Service port number |
| `N8N_POSTGRES_DB` | n8n | PostgreSQL database name |
| `N8N_POSTGRES_USER` | n8n | Service username |
| `N8N_PROTOCOL` |  | N8n protocol |
| `N8N_PROXY_HOPS` |  | N8n proxy hops |
| `N8N_RESTART` | unless-stopped | Container restart policy |
| `N8N_RUNNERS_ENABLED` |  | N8n runners enabled |
| `N8N_TRAEFIK_ENABLED` | true | Enable Traefik reverse proxy |
| `N8N_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `POSTGRES_PASSWORD_N8N` | n8n | Service password |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/n8n/:/home/node/.n8n/` - Volume mount
- `./media/n8n/workflows:/home/node/workflows` - Volume mount
- `${N8N_DATA_PATH:-./media/n8n}` - Data storage
- `./etc/n8n/postgresql:/var/lib/postgresql/data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${N8N_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.n8n.entrypoints=websecure`
- `traefik.http.routers.n8n.rule=Host(`${N8N_HOST_NAME:-n8n}.${HOST_DOMAIN}`)`
- `traefik.http.services.n8n.loadbalancer.server.port=${N8N_PORT:-5678}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${N8N_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${N8N_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${N8N_HOST_NAME:-n8n}.${HOST_DOMAIN}`

### Dependencies
This service depends on:
- `n8n_postgres`

## Quick Start

```bash
# Enable the service
make enable n8n

# Configure environment variables (if needed)
make scaffold n8n

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
- Requires n8n_postgres to be running
