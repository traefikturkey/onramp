# Sabnzbd

> Binary newsgrabber for usenet

## Links
- [Docker Image](https://hub.docker.com/r/linuxserver/sabnzbd)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/sabnzbd.yml)

## Docker Images
- `lscr.io/linuxserver/sabnzbd:${SABNZBD_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MEDIA_DOWNLOADS_VOLUME` | ./media/downloads | Media downloads volume |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `SABNZBD_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `SABNZBD_CONTAINER_NAME` | sabnzbd | Container name |
| `SABNZBD_DOCKER_TAG` | latest | Docker image tag/version |
| `SABNZBD_HAS_IPV6` | false | Sabnzbd has ipv6 |
| `SABNZBD_RESTART` | unless-stopped | Container restart policy |
| `SABNZBD_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `SABNZBD_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/sabnzbd:/config` - Volume mount
- `${MEDIA_DOWNLOADS_VOLUME:-./media/downloads}` - Volume mount
- `/dev/rtc:/dev/rtc` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${SABNZBD_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.sabnzbd.entrypoints=websecure`
- `traefik.http.routers.sabnzbd.rule=Host(`${SABNZBD_CONTAINER_NAME:-sabnzbd}.${HOST_DOMAIN}`)`
- `traefik.http.services.sabnzbd.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${SABNZBD_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${SABNZBD_AUTOHEAL:-true}`
- `joyride.host.name=${SABNZBD_CONTAINER_NAME:-sabnzbd}.${HOST_DOMAIN}`

## Available Overrides

OnRamp supports configuration overrides to customize this service. The following overrides are available:

### sabnzbd-gluetun

**Purpose**: Alternative configuration for this service

**Usage**:
```bash
make enable-override sabnzbd-gluetun
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/sabnzbd-gluetun.yml)

### sabnzbd-nfs

**Purpose**: Configures NFS volume mounts for remote storage

**Changes**:
- **Adds/modifies volumes**: `sabnzbd-nfs-downloads`
- **Adds/modifies services**: `sabnzbd`

**Usage**:
```bash
make enable-override sabnzbd-nfs
make up
```

**Configuration**: [View override file](https://github.com/traefikturkey/onramp/tree/main/overrides-available/sabnzbd-nfs.yml)

## Quick Start

```bash
# Enable the service
make enable sabnzbd

# Configure environment variables (if needed)
make scaffold sabnzbd

# Start the service
make up
```
