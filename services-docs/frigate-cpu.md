# Frigate Cpu

> frigate nvr with cpu only

## Links
- [Official Documentation](https://docs.frigate.video/frigate/installation/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/frigate-cpu.yml)

## Docker Images
- `ghcr.io/blakeblackshear/frigate:${FRIGATE_DOCKER_TAG:-stable}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FRIGATE_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `FRIGATE_CONTAINER_NAME` |  | Container name |
| `FRIGATE_DOCKER_TAG` |  | Docker image tag/version |
| `FRIGATE_HOST_NAME` |  | Frigate host name |
| `FRIGATE_MEDIA_PATH` |  | Frigate media path |
| `FRIGATE_MQTT_PASSWORD` |  | Service password |
| `FRIGATE_MQTT_USER` |  | Service username |
| `FRIGATE_PLUS_API_KEY` |  | Frigate plus api key |
| `FRIGATE_RESTART` |  | Container restart policy |
| `FRIGATE_RTSP_PASSWORD` |  | Service password |
| `FRIGATE_RTSP_USER` |  | Service username |
| `FRIGATE_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `FRIGATE_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/frigate:/config` - Volume mount
- `${FRIGATE_MEDIA_PATH:-./media/frigate}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `{'type': 'tmpfs', 'target'` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${FRIGATE_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.frigate.entrypoints=websecure`
- `traefik.http.routers.frigate.rule=Host(`${FRIGATE_HOST_NAME:-frigate}.${HOST_DOMAIN}`)`
- `traefik.http.services.frigate.loadbalancer.server.port=5000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FRIGATE_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${FRIGATE_AUTOHEAL:-true}`
- `joyride.host.name=${FRIGATE_HOST_NAME:-frigate}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### frigate-cpu-nfs

**Purpose**: Configures NFS volume mounts for CPU-based setup

**Changes**:
- **Adds/modifies volumes**: `frigate-cpu-nfs-media`
- **Adds/modifies services**: `frigate-cpu`

**Usage**:
```bash
make enable-override frigate-cpu-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/frigate-cpu-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable frigate-cpu

# Configure environment variables (if needed)
make scaffold frigate-cpu

# Start the service
make up
```
