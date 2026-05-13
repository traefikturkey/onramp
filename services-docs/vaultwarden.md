# Vaultwarden

> Self-hosted bitwarden password manager

## Links
- [Official Repository](https://github.com/dani-garcia/vaultwarden)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/vaultwarden.yml)

## Docker Images
- `ghcr.io/dani-garcia/vaultwarden:${VAULTWARDEN_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `VAULTWARDEN_ADMIN_TOKEN` | ${VAULTWARDEN_ADMIN_TOKEN:-} | Vaultwarden admin token |
| `VAULTWARDEN_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `VAULTWARDEN_CONTAINER_NAME` | vaultwarden | Container name |
| `VAULTWARDEN_DOCKER_TAG` | latest | Docker image tag/version |
| `VAULTWARDEN_HOSTNAME` | vaultwarden | Vaultwarden hostname |
| `VAULTWARDEN_MEM_LIMIT` | 200m | Vaultwarden mem limit |
| `VAULTWARDEN_SIGNUPS_ALLOWED` | true | Vaultwarden signups allowed |
| `VAULTWARDEN_SMTP_FROM` | vaultwarden@domain.tld | Vaultwarden smtp from |
| `VAULTWARDEN_SMTP_FROM_NAME` | Vaultwarden | Vaultwarden smtp from name |
| `VAULTWARDEN_SMTP_HOST` | smtp.domain.tld | Vaultwarden smtp host |
| `VAULTWARDEN_SMTP_PASSWORD` | password | Service password |
| `VAULTWARDEN_SMTP_PORT` | 587 | Service port number |
| `VAULTWARDEN_SMTP_SECURITY` | starttls | Vaultwarden smtp security |
| `VAULTWARDEN_SMTP_USERNAME` | username | Service username |
| `VAULTWARDEN_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `VAULTWARDEN_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/vaultwarden:/data` - Volume mount
- `/dev/rtc:/dev/rtc` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${VAULTWARDEN_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.vaultwarden.entrypoints=websecure`
- `traefik.http.routers.vaultwarden.rule=Host(`${VAULTWARDEN_HOSTNAME:-vaultwarden}.${HOST_DOMAIN}`)`
- `traefik.http.services.vaultwarden.loadbalancer.server.port=80`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${VAULTWARDEN_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${VAULTWARDEN_AUTOHEAL:-true}`
- `joyride.host.name=${VAULTWARDEN_HOSTNAME:-vaultwarden}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable vaultwarden

# Configure environment variables (if needed)
make scaffold vaultwarden

# Start the service
make up
```
