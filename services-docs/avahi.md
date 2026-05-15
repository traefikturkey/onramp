# Avahi

> Implements mdns/dns-sd for local network service discovery

## Links
- [Official Repository](https://github.com/flungo-docker/avahi)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/avahi.yml)

## Docker Images
- `flungo/avahi:${AVAHI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AVAHI_CONTAINER_NAME` |  | Container name |
| `AVAHI_DOCKER_TAG` |  | Docker image tag/version |
| `AVAHI_ENABLE_REFLECTOR` |  | Avahi enable reflector |
| `HOST_DOMAIN` |  | Host domain for service access |
| `HOST_NAME` |  | Host name |

## Configuration

### Volumes
- `/var/run/dbus/system_bus_socket:/var/run/dbus/system_bus_socket` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

## Quick Start

```bash
# Enable the service
make enable avahi

# Configure environment variables (if needed)
make scaffold avahi

# Start the service
make up
```
