# Cv4Pve

> managment and monitoring solution for proxmox virtual environment (pve)

## Links
- [Official Repository](https://github.com/Corsinvest/cv4pve-admin/tree/main)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/cv4pve.yml)

## Docker Images
- `corsinvest/cv4pve-admin:${CV4PVE_DOCKER_TAG:-1.0.2}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CV4PVE_CONTAINER_NAME` |  | Container name |
| `CV4PVE_DOCKER_TAG` |  | Docker image tag/version |
| `CV4PVE_RESTART` |  | Container restart policy |
| `CV4PVE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/cv4pve/data:/app/data` - Data storage
- `./etc/cv4pve/appsettings.json:/app/appsettings.json` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.cv4pve.entrypoints=websecure`
- `traefik.http.routers.cv4pve.rule=Host(`${CV4PVE_CONTAINER_NAME:-cv4pve}.${HOST_DOMAIN}`)`
- `traefik.http.services.cv4pve.loadbalancer.server.port=5000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CV4PVE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${CV4PVE_CONTAINER_NAME:-cv4pve}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable cv4pve

# Configure environment variables (if needed)
make scaffold cv4pve

# Start the service
make up
```
