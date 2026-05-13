# Beszel Agent

> agent to connect to the Beszel hub for monitoring of docker containers and servers.

## Links
- [Official Repository](https://github.com/henrygd/beszel)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/beszel-agent.yml)

## Docker Images
- `ghcr.io/henrygd/beszel/beszel-agent:${BESZEL_AGENT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BESZEL_AGENT_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `BESZEL_AGENT_CONTAINER_NAME` |  | Container name |
| `BESZEL_AGENT_DOCKER_TAG` |  | Docker image tag/version |
| `BESZEL_AGENT_RESTART` |  | Container restart policy |
| `BESZEL_AGENT_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `BESZEL_AGENT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `BESZEL_PUBLIC_KEY` |  | Beszel public key |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/beszel-agent:/beszel_socket` - Volume mount
- `/var/run/docker.sock:/var/run/docker.sock` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=${BESZEL_AGENT_TRAEFIK_ENABLED:-false}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${BESZEL_AGENT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${BESZEL_AGENT_AUTOHEAL_ENABLED:-true}`

## Quick Start

```bash
# Enable the service
make enable beszel-agent

# Configure environment variables (if needed)
make scaffold beszel-agent

# Start the service
make up
```
