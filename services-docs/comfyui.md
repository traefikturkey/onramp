# Comfyui

> ComfyUI with FLUX.1 models

## Links
- [Official Repository](https://github.com/comfyanonymous/ComfyUI)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/comfyui.yml)

## Docker Images
- `frefrik/comfyui-flux:${COMFYUI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `COMFYUI_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `COMFYUI_CONTAINER_NAME` |  | Container name |
| `COMFYUI_DATA_DIR` |  | Data directory path |
| `COMFYUI_DOCKER_TAG` |  | Docker image tag/version |
| `COMFYUI_HOST_NAME` |  | Comfyui host name |
| `COMFYUI_MEM_LIMIT` |  | Comfyui mem limit |
| `COMFYUI_RESTART` |  | Container restart policy |
| `COMFYUI_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `COMFYUI_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HF_TOKEN` |  | Hf token |
| `HOST_DOMAIN` |  | Host domain for service access |
| `LOW_VRAM` |  | Low vram |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${COMFYUI_DATA_DIR:-./etc/comfyui}` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${COMFYUI_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.comfyui.entrypoints=websecure`
- `traefik.http.routers.comfyui.rule=Host(`${COMFYUI_HOST_NAME:-comfyui}.${HOST_DOMAIN}`)`
- `traefik.http.services.comfyui.loadbalancer.server.port=8188`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${COMFYUI_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${COMFYUI_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${COMFYUI_HOST_NAME:-comfyui}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable comfyui

# Configure environment variables (if needed)
make scaffold comfyui

# Start the service
make up
```
