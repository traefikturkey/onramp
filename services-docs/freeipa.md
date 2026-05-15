# Freeipa

> FreeIPA server container (systemd-based)

## Links
- [Official Repository](https://github.com/freeipa/freeipa-container)
- [Official Documentation](https://quay.io/repository/freeipa/freeipa-server)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/freeipa.yml)

## Docker Images
- `freeipa/freeipa-server:${FREEIPA_DOCKER_TAG:-rocky-9}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `FREEIPA_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `FREEIPA_CONTAINER_NAME` | freeipa | Container name |
| `FREEIPA_DOCKER_TAG` | latest | Docker image tag/version |
| `FREEIPA_EXPOSE_PORTS` | false | Service port number |
| `FREEIPA_RESTART` | unless-stopped | Container restart policy |
| `FREEIPA_SERVER_HOSTNAME` | ${FREEIPA_SERVER_HOSTNAME} | Freeipa server hostname |
| `FREEIPA_SERVER_INSTALL_OPTS` | ${FREEIPA_SERVER_INSTALL_OPTS} | Freeipa server install opts |
| `FREEIPA_SERVER_IP` | ${FREEIPA_SERVER_IP} | Freeipa server ip |
| `FREEIPA_SERVER_PASSWORD` | ${FREEIPA_SERVER_PASSWORD} | Service password |
| `FREEIPA_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |

## Configuration

### Volumes
- `./etc/freeipa:/data` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${FREEIPA_WATCHTOWER_ENABLED:-false}`

**Other Labels:**
- `autoheal=${FREEIPA_AUTOHEAL_ENABLED:-false}`
- `joyride.host.name=${FREEIPA_CONTAINER_NAME:-freeipa}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable freeipa

# Configure environment variables (if needed)
make scaffold freeipa

# Start the service
make up
```
