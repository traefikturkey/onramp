# Claude Connector

> Shared MCP memory server for Claude Code and Claude.ai

## Links
- [Official Repository](https://github.com/crack-kitty/claudememkeep)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/claude-connector.yml)

## Docker Images
- `ghcr.io/crack-kitty/claudememkeep:${CLAUDE_CONNECTOR_IMAGE_TAG:-latest}`
- `postgres:${CLAUDE_CONNECTOR_POSTGRES_TAG:-16-alpine}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_CONNECTOR_AUTH_TOKEN` | ${CLAUDE_CONNECTOR_AUTH_TOKEN} | Claude connector auth token |
| `CLAUDE_CONNECTOR_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `CLAUDE_CONNECTOR_CONTAINER_NAME` | claude-connector | Container name |
| `CLAUDE_CONNECTOR_DB_CONTAINER_NAME` | claude-connector-db | Container name |
| `CLAUDE_CONNECTOR_DB_HOST` | claude-connector-db | Claude connector db host |
| `CLAUDE_CONNECTOR_DB_NAME` | claude_connector | Claude connector db name |
| `CLAUDE_CONNECTOR_DB_PASSWORD` | ${CLAUDE_CONNECTOR_DB_PASSWORD} | Service password |
| `CLAUDE_CONNECTOR_DB_PORT` | 5432 | Service port number |
| `CLAUDE_CONNECTOR_DB_USER` | claude_connector | Service username |
| `CLAUDE_CONNECTOR_HOST_NAME` | claude-connector | Claude connector host name |
| `CLAUDE_CONNECTOR_IMAGE_TAG` |  | Claude connector image tag |
| `CLAUDE_CONNECTOR_POSTGRES_TAG` | 16-alpine | Claude connector postgres tag |
| `CLAUDE_CONNECTOR_RESTART` | unless-stopped | Container restart policy |
| `CLAUDE_CONNECTOR_TRAEFIK_ENABLED` | true | Enable Traefik reverse proxy |
| `CLAUDE_CONNECTOR_WATCHTOWER_ENABLED` | false | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Volumes
- `/apps/onramp/etc/claude-connector/pgdata:/var/lib/postgresql/data` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CLAUDE_CONNECTOR_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.claude-connector.entrypoints=websecure`
- `traefik.http.routers.claude-connector.rule=Host(`${CLAUDE_CONNECTOR_HOST_NAME:-claude-connector}.${HOST_DOMAIN}`)`
- `traefik.http.services.claude-connector.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CLAUDE_CONNECTOR_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${CLAUDE_CONNECTOR_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${CLAUDE_CONNECTOR_HOST_NAME:-claude-connector}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable claude-connector

# Configure environment variables (if needed)
make scaffold claude-connector

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
