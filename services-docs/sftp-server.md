# Sftp Server

> Secure ftp server

## Links
- [Official Repository](https://github.com/drakkan/sftpgo)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/sftp-server.yml)

## Docker Images
- `ghcr.io/drakkan/sftpgo:${SFTP_SERVER_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SFTP_SERVER_CONTAINER_NAME` |  | Container name |
| `SFTP_SERVER_DOCKER_TAG` |  | Docker image tag/version |
| `SFTP_SERVER_PORT` |  | Service port number |
| `SFTP_SERVER_RESTART` |  | Container restart policy |
| `SFTP_SERVER_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `${SFTP_SERVER_PORT:-7222:2022}`

### Volumes
- `./etc/sftp-server:/var/lib/sftpgo` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.sftp-server.entrypoints=websecure`
- `traefik.http.routers.sftp-server.rule=Host(`${SFTP_SERVER_CONTAINER_NAME:-sftp-server}.${HOST_DOMAIN}`)`
- `traefik.http.services.sftp-server.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SFTP_SERVER_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${SFTP_SERVER_CONTAINER_NAME:-sftp-server}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable sftp-server

# Configure environment variables (if needed)
make scaffold sftp-server

# Start the service
make up
```
