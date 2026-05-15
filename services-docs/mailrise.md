# Mailrise

> email smtp relay service for apprise notifications

## Links
- [Official Repository](https://github.com/YoRyan/mailrise)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mailrise.yml)

## Docker Images
- `yoryan/mailrise:${MAILRISE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MAILRISE_CONTAINER_NAME` |  | Container name |
| `MAILRISE_DOCKER_TAG` |  | Docker image tag/version |
| `MAILRISE_PORT` |  | Service port number |
| `MAILRISE_RESTART` |  | Container restart policy |
| `MAILRISE_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Ports
- `${MAILRISE_PORT:-8025}:8025`

### Volumes
- `./etc/mailrise/mailrise.conf:/etc/mailrise.conf` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.tcp.routers.mailrise.entrypoints=mailsecure`
- `traefik.tcp.routers.mailrise.rule=HostSNI(`${MAILRISE_CONTAINER_NAME:-mailrise}.${HOST_DOMAIN}`)`
- `traefik.tcp.routers.mailrise.tls=true`
- `traefik.tcp.routers.mailrise.tls.certresolver=letsencrypt`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MAILRISE_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${MAILRISE_CONTAINER_NAME:-mailrise}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable mailrise

# Configure environment variables (if needed)
make scaffold mailrise

# Start the service
make up
```
