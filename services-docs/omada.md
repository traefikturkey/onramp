# Omada

> Container for running tp-link omada controller

## Links
- [Official Repository](https://github.com/mbentley/docker-omada-controller?tab=readme-ov-file#v5-to-v6-upgrade-guide)
- [Docker Image](https://hub.docker.com/r/mbentley/omada-controller)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/omada.yml)

## Docker Images
- `mbentley/omada-controller:${OMADA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OMADA_CONTAINER_NAME` |  | Container name |
| `OMADA_DOCKER_TAG` |  | Docker image tag/version |
| `OMADA_MANAGE_HTTPS_PORT` |  | Service port number |
| `OMADA_MANAGE_HTTP_PORT` |  | Service port number |
| `OMADA_MEM_LIMIT` |  | Omada mem limit |
| `OMADA_PORTAL_HTTPS_PORT` |  | Service port number |
| `OMADA_PORTAL_HTTP_PORT` |  | Service port number |
| `OMADA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `8088:8088`
- `8043:8043`
- `8843:8843`
- `19810:19810/udp`
- `27001:27001/udp`
- `29810:29810/udp`
- `29811-29817:29811-29817`

### Volumes
- `./etc/omada/data:/opt/tplink/EAPController/data` - Data storage
- `./etc/omada/work:/opt/tplink/EAPController/work` - Volume mount
- `./etc/omada/logs:/opt/tplink/EAPController/logs` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.omada.entrypoints=websecure`
- `traefik.http.routers.omada.rule=Host(`${OMADA_CONTAINER_NAME:-omada}.${HOST_DOMAIN}`)`
- `traefik.http.services.omada.loadbalancer.server.port=8043`
- `traefik.http.services.omada.loadbalancer.server.scheme=https`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OMADA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${OMADA_CONTAINER_NAME:-omada}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable omada

# Configure environment variables (if needed)
make scaffold omada

# Start the service
make up
```
