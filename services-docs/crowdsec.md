# Crowdsec

> Detects and blocks malicious behavior on servers

## Links
- [Official Repository](https://github.com/crowdsecurity/crowdsec)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/crowdsec.yml)

## Docker Images
- `ghcr.io/crowdsecurity/crowdsec:${CROWDSEC_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CROWDSEC_CONTAINER_NAME` |  | Container name |
| `CROWDSEC_DOCKER_TAG` |  | Docker image tag/version |
| `CROWDSEC_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/crowdsec:/etc/crowdsec/` - Volume mount
- `./etc/crowdsec/db:/var/lib/crowdsec/data/` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CROWDSEC_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable crowdsec

# Configure environment variables (if needed)
make scaffold crowdsec

# Start the service
make up
```
