# Joplin Api

> Headless Joplin with Web Clipper API

## Links
- [Official Repository](https://github.com/RickoNoNo3/joplin-terminal-data-api)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/joplin-api.yml)

## Docker Images
- `rickonono3/joplin-terminal-data-api:${JOPLIN_API_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `JOPLIN_API_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `JOPLIN_API_CONTAINER_NAME` | joplin-api | Container name |
| `JOPLIN_API_DOCKER_TAG` | latest | Docker image tag/version |
| `JOPLIN_API_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `JOPLIN_PASSWORD` | ${JOPLIN_PASSWORD} | Service password |
| `JOPLIN_SERVER_URL` | ${JOPLIN_SERVER_URL:-} | Joplin server url |
| `JOPLIN_USERNAME` | ${JOPLIN_USERNAME:-} | Service username |

## Configuration

### Volumes
- `./etc/joplin-api/config:/root/joplin` - Configuration files
- `./etc/joplin-api/data:/root/.config/joplin` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=false`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${JOPLIN_API_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${JOPLIN_API_AUTOHEAL:-true}`

## Quick Start

```bash
# Enable the service
make enable joplin-api

# Configure environment variables (if needed)
make scaffold joplin-api

# Start the service
make up
```
