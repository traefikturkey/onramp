# Youtube Transcript Mcp

> Model Context Protocol server that retrieves YouTube video transcripts

## Links
- [Official Repository](https://github.com/jkawamoto/mcp-youtube-transcript)
- [Docker Image](https://hub.docker.com/r/mcp/youtube-transcript)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/youtube-transcript-mcp.yml)

## Docker Images
- `mcp/youtube-transcript:${YOUTUBE_TRANSCRIPT_MCP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `TZ` |  | Timezone setting |
| `YOUTUBE_TRANSCRIPT_MCP_AUTOHEAL` |  | Enable Autoheal container restart on unhealthy status |
| `YOUTUBE_TRANSCRIPT_MCP_CONTAINER_NAME` |  | Container name |
| `YOUTUBE_TRANSCRIPT_MCP_DOCKER_TAG` |  | Docker image tag/version |
| `YOUTUBE_TRANSCRIPT_MCP_HOST_NAME` |  | Youtube transcript mcp host name |
| `YOUTUBE_TRANSCRIPT_MCP_MEM_LIMIT` |  | Youtube transcript mcp mem limit |
| `YOUTUBE_TRANSCRIPT_MCP_PORT` |  | Service port number |
| `YOUTUBE_TRANSCRIPT_MCP_RESTART` |  | Container restart policy |
| `YOUTUBE_TRANSCRIPT_MCP_TRAEFIK_ENABLE` |  | Enable Traefik reverse proxy |
| `YOUTUBE_TRANSCRIPT_MCP_WATCHTOWER_ENABLE` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${YOUTUBE_TRANSCRIPT_MCP_TRAEFIK_ENABLE:-true}`
- `traefik.http.routers.youtube-transcript-mcp.entrypoints=websecure`
- `traefik.http.routers.youtube-transcript-mcp.rule=Host(`${YOUTUBE_TRANSCRIPT_MCP_HOST_NAME:-youtube-transcript}.${HOST_DOMAIN}`)`
- `traefik.http.services.youtube-transcript-mcp.loadbalancer.server.port=${YOUTUBE_TRANSCRIPT_MCP_PORT:-8080}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${YOUTUBE_TRANSCRIPT_MCP_WATCHTOWER_ENABLE:-true}`

**Other Labels:**
- `autoheal=${YOUTUBE_TRANSCRIPT_MCP_AUTOHEAL:-true}`
- `joyride.host.name=${YOUTUBE_TRANSCRIPT_MCP_HOST_NAME:-youtube-transcript}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable youtube-transcript-mcp

# Configure environment variables (if needed)
make scaffold youtube-transcript-mcp

# Start the service
make up
```
