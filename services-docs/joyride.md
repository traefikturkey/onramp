# Joyride

> dns server using docker labels

## Links
- [Official Repository](https://github.com/traefikturkey/joyride/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/joyride.yml)

## Docker Images
- `ghcr.io/traefikturkey/joyride:${JOYRIDE_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLUSTER_ENABLED` | false | Cluster enabled |
| `DNS_UNKNOWN_ACTION` | drop | Dns unknown action |
| `HOSTIP` |  | Hostip |
| `JOYRIDE_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `JOYRIDE_CONTAINER_NAME` | joyride | Container name |
| `JOYRIDE_DOCKER_TAG` | latest | Docker image tag/version |
| `JOYRIDE_MEM_LIMIT` | 128m | Joyride mem limit |
| `JOYRIDE_RESTART` | unless-stopped | Container restart policy |
| `JOYRIDE_TRAEFIK_ENABLE` | false | Enable Traefik reverse proxy |
| `JOYRIDE_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount
- `./etc/joyride/hosts.d:/etc/hosts.d` - Volume mount
- `./external-enabled:/etc/traefik/external-enabled` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=${JOYRIDE_TRAEFIK_ENABLE:-false}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${JOYRIDE_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${JOYRIDE_AUTOHEAL:-true}`

## Quick Start

```bash
# Enable the service
make enable joyride

# Configure environment variables (if needed)
make scaffold joyride

# Start the service
make up
```
