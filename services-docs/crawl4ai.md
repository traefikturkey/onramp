# Crawl4Ai

> LLM-friendly web crawler and scraper with a Docker API server

## Links
- [Official Repository](https://github.com/unclecode/crawl4ai)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/crawl4ai.yml)

## Docker Images
- `unclecode/crawl4ai:${CRAWL4AI_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRAWL4AI_API_TOKEN` | change-me | **Required** — API authentication token. Without it, the server binds loopback-only and is unreachable via Traefik. Obtain from [crawl4ai](https://github.com/unclecode/crawl4ai).
| `CRAWL4AI_AUTOHEAL` | true | Enable Autoheal container restart on unhealthy status |
| `CRAWL4AI_CONTAINER_NAME` | crawl4ai | Container name |
| `CRAWL4AI_DOCKER_TAG` | latest | Docker image tag/version |
| `CRAWL4AI_HOST_NAME` | crawl4ai | Crawl4ai host name |
| `CRAWL4AI_RESTART` | unless-stopped | Container restart policy |
| `CRAWL4AI_TRAEFIK_ENABLE` | true | Enable Traefik reverse proxy |
| `CRAWL4AI_WATCHTOWER_ENABLE` | true | Enable Watchtower auto-updates |
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${CRAWL4AI_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.crawl4ai.entrypoints=websecure`
- ``traefik.http.routers.crawl4ai.rule=Host(`${CRAWL4AI_HOST_NAME:-crawl4ai}.${HOST_DOMAIN}`)``
- `traefik.http.services.crawl4ai.loadbalancer.server.port=11235`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${CRAWL4AI_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${CRAWL4AI_AUTOHEAL:-true}`
- `joyride.host.name=${CRAWL4AI_HOST_NAME:-crawl4ai}.${HOST_DOMAIN}`

## Quick Start

Crawl4ai v0.9.x enables authentication by default. You **must** set `CRAWL4AI_API_TOKEN` to a non-empty value for the service to be accessible externally via Traefik. Without a token, the server binds to `127.0.0.1` only.

Generate a token (e.g., `openssl rand -hex 32`) or use your Crawl4.ai cloud token:
```bash
# Enable the service
make enable crawl4ai

# Set your API token
make edit-env crawl4ai
# Change CRAWL4AI_API_TOKEN=change-me → CRAWL4AI_API_TOKEN=<your-token>

# Start the service
make up
```
