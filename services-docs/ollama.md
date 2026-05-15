# Ollama

> Easy way to run large language models locally - Nvidia GPU

## Links
- [Official Repository](https://github.com/ollama/ollama)
- [Docker Image](https://hub.docker.com/r/ollama/ollama)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/ollama.yml)

## Docker Images
- `ollama/ollama:${OLLAMA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OLLAMA_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `OLLAMA_CONTAINER_NAME` |  | Container name |
| `OLLAMA_DATA_PATH` |  | Ollama data path |
| `OLLAMA_DOCKER_TAG` |  | Docker image tag/version |
| `OLLAMA_PORT` |  | Service port number |
| `OLLAMA_RESTART` |  | Container restart policy |
| `OLLAMA_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `OLLAMA_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${OLLAMA_PORT:-11434}:11434`

### Volumes
- `${OLLAMA_DATA_PATH:-./media/ollama}` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${OLLAMA_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.ollama.entrypoints=websecure`
- `traefik.http.routers.ollama.rule=Host(`${OLLAMA_CONTAINER_NAME:-ollama}.${HOST_DOMAIN}`)`
- `traefik.http.services.ollama.loadbalancer.server.port=11434`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OLLAMA_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${OLLAMA_AUTOHEAL:-true}`
- `joyride.host.name=${OLLAMA_CONTAINER_NAME:-ollama}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### ollama-amd

**Purpose**: Enables AMD GPU hardware acceleration

**Changes**:
- **Adds/modifies services**: `ollama`

**Usage**:
```bash
make enable-override ollama-amd
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/ollama-amd.yml)

### ollama-nvidia

**Purpose**: Enables NVIDIA GPU hardware acceleration

**Changes**:
- **Adds/modifies services**: `ollama`
- **Adds/modifies environment variables**: `PUID`, `PGID`, `TZ`, `gpus`

**Usage**:
```bash
make enable-override ollama-nvidia
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/ollama-nvidia.yml)

## Quick Start

```bash
# Enable the service
make enable ollama

# Configure environment variables (if needed)
make scaffold ollama

# Start the service
make up
```
