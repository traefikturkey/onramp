# Authelia

> Provides single sign-on (sso) and two-factor authentication (2fa) for web applications

## Links
- [Official Repository](https://github.com/authelia/authelia)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/authelia.yml)

## Docker Images
- `ghcr.io/authelia/authelia:${AUTHELIA_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTHELIA_AUTH_DOMAIN` |  | Authelia auth domain |
| `AUTHELIA_DOCKER_TAG` |  | Docker image tag/version |
| `AUTHELIA_JWT_SECRET` |  | Authelia jwt secret |
| `AUTHELIA_REDIR_DOMAIN` |  | Authelia redir domain |
| `AUTHELIA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Ports
- `9091 (internal)`

### Volumes
- `./etc/authelia:/config` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=true`
- `traefik.http.middlewares.authelia.forwardauth.address=http://authelia:9091/api/verify?rd=${AUTHELIA_REDIR_DOMAIN}`
- `traefik.http.middlewares.authelia.forwardauth.authResponseHeaders=Remote-User,Remote-Groups,Remote-Name,Remote-Email`
- `traefik.http.middlewares.authelia.forwardauth.trustForwardHeader=true`
- `traefik.http.routers.authelia.entrypoints=websecure`
- `traefik.http.routers.authelia.rule=Host(`${AUTHELIA_AUTH_DOMAIN}`)`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${AUTHELIA_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=${AUTHELIA_AUTH_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable authelia

# Configure environment variables (if needed)
make scaffold authelia

# Start the service
make up
```
