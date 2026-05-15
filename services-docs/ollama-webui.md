# Ollama Webui

> Web-based user interface for ollama LLM and others

## Links
- [Official Repository](https://github.com/open-webui/open-webui)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/ollama-webui.yml)

## Docker Images
- `ghcr.io/open-webui/open-webui:${OLLAMA_WEBUI_DOCKER_TAG:-main}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OLLAMA_CONTAINER_NAME` |  | Container name |
| `OLLAMA_WEBUI_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `OLLAMA_WEBUI_CONTAINER_NAME` |  | Container name |
| `OLLAMA_WEBUI_DOCKER_TAG` |  | Docker image tag/version |
| `OLLAMA_WEBUI_RESTART` |  | Container restart policy |
| `OLLAMA_WEBUI_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `OLLAMA_WEBUI_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/ollama-webui:/app/backend/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${OLLAMA_WEBUI_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.ollama-webui.entrypoints=websecure`
- `traefik.http.routers.ollama-webui.rule=Host(`${OLLAMA_WEBUI_CONTAINER_NAME:-chat}.${HOST_DOMAIN}`)`
- `traefik.http.services.ollama-webui.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OLLAMA_WEBUI_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${OLLAMA_WEBUI_AUTOHEAL:-true}`
- `joyride.host.name=${OLLAMA_WEBUI_CONTAINER_NAME:-chat}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable ollama-webui

# Configure environment variables (if needed)
make scaffold ollama-webui

# Start the service
make up
```
