# Mosquitto

> N mqtt broker for iot communication

## Links
- [Docker Image](https://hub.docker.com/_/eclipse-mosquitto)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/mosquitto.yml)

## Docker Images
- `eclipse-mosquitto:${MOSQITTO_MQTT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `MOSQITTO_MQTT_DOCKER_TAG` |  | Docker image tag/version |
| `MOSQUITTO_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |

## Configuration

### Ports
- `1883:1883`
- `9002:9001`

### Volumes
- `./etc/mosquitto/config:/mosquitto/config` - Configuration files
- `./etc/mosquitto/data:/mosquitto/data` - Data storage
- `./etc/mosquitto/log:/mosquitto/log` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${MOSQUITTO_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=true`
- `joyride.host.name=mqtt.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable mosquitto

# Configure environment variables (if needed)
make scaffold mosquitto

# Start the service
make up
```
