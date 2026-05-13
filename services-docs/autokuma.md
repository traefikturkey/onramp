# Autokuma

> Automate the setup of Uptime Kuma using docker labels

## Links
- [Official Repository](https://github.com/BigBoot/AutoKuma)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/autokuma.yml)

## Docker Images
- `ghcr.io/bigboot/autokuma:${AUTOKUMA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTOKUMA_CONTAINER_NAME` |  | Container name |
| `AUTOKUMA_DOCKER_LABEL_PREFIX` |  | Autokuma docker label prefix |
| `AUTOKUMA_DOCKER_SOCKET` |  | Autokuma docker socket |
| `AUTOKUMA_DOCKER_TAG` |  | Docker image tag/version |
| `AUTOKUMA_KUMA_CALL_TIMEOUT` |  | Autokuma kuma call timeout |
| `AUTOKUMA_KUMA_CONNECT_TIMEOUT` |  | Autokuma kuma connect timeout |
| `AUTOKUMA_KUMA_HEADERS` |  | Autokuma kuma headers |
| `AUTOKUMA_KUMA_MFA_TOKEN` |  | Autokuma kuma mfa token |
| `AUTOKUMA_KUMA_PASSWORD` |  | Service password |
| `AUTOKUMA_KUMA_TAG_COLOR` |  | Autokuma kuma tag color |
| `AUTOKUMA_KUMA_TAG_NAME` |  | Autokuma kuma tag name |
| `AUTOKUMA_KUMA_URL` |  | Autokuma kuma url |
| `AUTOKUMA_KUMA_USERNAME` |  | Service username |
| `AUTOKUMA_RESTART` |  | Container restart policy |
| `AUTOKUMA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${AUTOKUMA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`

## Quick Start

```bash
# Enable the service
make enable autokuma

# Configure environment variables (if needed)
make scaffold autokuma

# Start the service
make up
```
