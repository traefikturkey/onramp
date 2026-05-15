# Postfix

> Mail transfer agent (mta) for sending and receiving emails

## Links
- [Official Repository](https://github.com/juanluisbaptiste/docker-postfix)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/postfix.yml)

## Docker Images
- `juanluisbaptiste/postfix:${POSTFIX_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `POSTFIX_CONTAINER_NAME` | postfix | Container name |
| `POSTFIX_DOCKER_TAG` | latest | Docker image tag/version |
| `POSTFIX_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |
| `PUID` |  | User ID for file permissions |
| `SERVER_HOSTNAME` | mail.${HOST_DOMAIN | Server hostname |
| `SMTP_PASSWORD` | changeme | Service password |
| `SMTP_PORT` | 587 | Service port number |
| `SMTP_SERVER` | smtp.example.com | Smtp server |
| `SMTP_USERNAME` | user@example.com | Service username |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `1525`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${POSTFIX_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${POSTFIX_CONTAINER_NAME:-postfix}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable postfix

# Configure environment variables (if needed)
make scaffold postfix

# Start the service
make up
```
