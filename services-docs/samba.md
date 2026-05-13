# Samba

> Provides file and print services for windows clients

## Links
- [Official Repository](https://github.com/ServerContainers/samba)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/samba.yml)

## Docker Images
- `ghcr.io/servercontainers/samba:${SAMBA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SAMBA_CONTAINER_NAME` |  | Container name |
| `SAMBA_DOCKER_TAG` |  | Docker image tag/version |
| `SAMBA_PASSWORD` |  | Service password |
| `SAMBA_SHARE1_NAME` |  | Samba share1 name |
| `SAMBA_SHARE1_VOLUME` |  | Samba share1 volume |
| `SAMBA_USER` |  | Service username |
| `SAMBA_WORKGROUP` |  | Samba workgroup |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${SAMBA_SHARE1_VOLUME:-./media}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

## Quick Start

```bash
# Enable the service
make enable samba

# Configure environment variables (if needed)
make scaffold samba

# Start the service
make up
```
