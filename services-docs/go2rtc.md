# Go2Rtc

> Webrtc gateway for camera restreaming

## Links
- [Official Repository](https://github.com/AlexxIT/go2rtc)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/go2rtc.yml)

## Docker Images
- `ghcr.io/alexxit/go2rtc:${GO2RTC_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GO2RTC_CONTAINER_NAME` |  | Container name |
| `GO2RTC_DOCKER_TAG` |  | Docker image tag/version |
| `GO2RTC_RESTART` |  | Container restart policy |
| `GO2RTC_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/go2rtc:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.routers.go2rtc.entrypoints=websecure`
- `traefik.http.routers.go2rtc.rule=Host(`${GO2RTC_CONTAINER_NAME:-go2rtc}.${HOST_DOMAIN}`)`
- `traefik.http.services.go2rtc.loadbalancer.server.port=1984`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GO2RTC_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${GO2RTC_CONTAINER_NAME:-go2rtc}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable go2rtc

# Configure environment variables (if needed)
make scaffold go2rtc

# Start the service
make up
```
