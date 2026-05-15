# N8N Mcp

> MCP server for n8n node documentation and workflow management

## Links
- [Official Repository](https://github.com/czlonkowski/n8n-mcp)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/n8n-mcp.yml)

## Docker Images
- `ghcr.io/czlonkowski/n8n-mcp:${N8N_MCP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `N8N_HOST_NAME` |  | N8n host name |
| `N8N_MCP_AUTH_TOKEN` | ${N8N_MCP_AUTH_TOKEN:-} | N8n mcp auth token |
| `N8N_MCP_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `N8N_MCP_CONTAINER_NAME` | n8n-mcp | Container name |
| `N8N_MCP_DOCKER_TAG` | latest | Docker image tag/version |
| `N8N_MCP_HOST_NAME` | n8n-mcp | N8n mcp host name |
| `N8N_MCP_LOG_LEVEL` | info | N8n mcp log level |
| `N8N_MCP_MEM_LIMIT` | 512m | N8n mcp mem limit |
| `N8N_MCP_N8N_API_KEY` | ${N8N_MCP_N8N_API_KEY:-} | N8n mcp n8n api key |
| `N8N_MCP_RESTART` | unless-stopped | Container restart policy |
| `N8N_MCP_TRAEFIK_ENABLED` | true | Enable Traefik reverse proxy |
| `N8N_MCP_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${N8N_MCP_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.n8n-mcp.entrypoints=websecure`
- `traefik.http.routers.n8n-mcp.rule=Host(`${N8N_MCP_HOST_NAME:-n8n-mcp}.${HOST_DOMAIN}`)`
- `traefik.http.services.n8n-mcp.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${N8N_MCP_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${N8N_MCP_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${N8N_MCP_HOST_NAME:-n8n-mcp}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable n8n-mcp

# Configure environment variables (if needed)
make scaffold n8n-mcp

# Start the service
make up
```
