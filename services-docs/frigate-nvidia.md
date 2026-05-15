# Frigate Nvidia

> Container for running frigate with nvidia gpu support

## Links
- [Official Documentation](https://docs.frigate.video/frigate/installation/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/frigate-nvidia.yml)

## Docker Images
- `ghcr.io/blakeblackshear/frigate:${FRIGATE_DOCKER_TAG:-stable-tensorrt}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FRIGATE_CONTAINER_NAME` |  | Container name |
| `FRIGATE_DOCKER_TAG` |  | Docker image tag/version |
| `FRIGATE_MEDIA_PATH` |  | Frigate media path |
| `FRIGATE_MQTT_PASSWORD` |  | Service password |
| `FRIGATE_MQTT_USER` |  | Service username |
| `FRIGATE_PLUS_API_KEY` |  | Frigate plus api key |
| `FRIGATE_RESTART` |  | Container restart policy |
| `FRIGATE_RTSP_PASSWORD` |  | Service password |
| `FRIGATE_RTSP_USER` |  | Service username |
| `FRIGATE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `8554:8554`
- `8555:8555/tcp`
- `8555:8555/udp`

### Volumes
- `./etc/frigate:/config` - Volume mount
- `${FRIGATE_MEDIA_PATH:-./media/frigate}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `{'type': 'tmpfs', 'target'` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.frigate.entrypoints=websecure`
- `traefik.http.routers.frigate.rule=Host(`${FRIGATE_CONTAINER_NAME:-frigate}.${HOST_DOMAIN}`)`
- `traefik.http.services.frigate.loadbalancer.server.port=5000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FRIGATE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${FRIGATE_CONTAINER_NAME:-frigate}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### frigate-nvidia-nfs

**Purpose**: Configures NFS volume mounts for NVIDIA GPU setup

**Changes**:
- **Adds/modifies volumes**: `frigate-nvidia-nfs-media`
- **Adds/modifies services**: `frigate-nvidia`

**Usage**:
```bash
make enable-override frigate-nvidia-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/frigate-nvidia-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable frigate-nvidia

# Configure environment variables (if needed)
make scaffold frigate-nvidia

# Start the service
make up
```
