# Karakeep

> A self-hostable bookmark-everything app (links, notes and images) with AI-based automatic tagging and full text search

## Links
- [Official Repository](https://github.com/karakeep-app/karakeep)
- [Official Documentation](https://docs.karakeep.app/)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/karakeep.yml)

## Docker Images
- `ghcr.io/karakeep-app/karakeep:${KARAKEEP_VERSION:-release}`
- `gcr.io/zenika-hub/alpine-chrome:123`
- `getmeili/meilisearch:v1.13.3`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `KARAKEEP_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `KARAKEEP_CONTAINER_NAME` |  | Container name |
| `KARAKEEP_DISABLE_SIGNUPS` |  | Karakeep disable signups |
| `KARAKEEP_EMBEDDING_TEXT_MODEL` |  | Karakeep embedding text model |
| `KARAKEEP_HOST_NAME` |  | Karakeep host name |
| `KARAKEEP_INFERENCE_CONTEXT_LENGTH` |  | Karakeep inference context length |
| `KARAKEEP_INFERENCE_IMAGE_MODEL` |  | Karakeep inference image model |
| `KARAKEEP_INFERENCE_LANG` |  | Karakeep inference lang |
| `KARAKEEP_INFERENCE_TEXT_MODEL` |  | Karakeep inference text model |
| `KARAKEEP_MAX_ASSET_SIZE` |  | Karakeep max asset size |
| `KARAKEEP_MEILI_MASTER_KEY` |  | Karakeep meili master key |
| `KARAKEEP_MEILI_NO_ANALYTICS` |  | Karakeep meili no analytics |
| `KARAKEEP_MEM_LIMIT` |  | Karakeep mem limit |
| `KARAKEEP_NEXTAUTH_SECRET` |  | Karakeep nextauth secret |
| `KARAKEEP_OAUTH_CLIENT_ID` |  | Karakeep oauth client id |
| `KARAKEEP_OAUTH_CLIENT_SECRET` |  | Karakeep oauth client secret |
| `KARAKEEP_OAUTH_PROVIDER_NAME` |  | Karakeep oauth provider name |
| `KARAKEEP_OAUTH_WELLKNOWN_URL` |  | Karakeep oauth wellknown url |
| `KARAKEEP_OLLAMA_KEEPALIVE` |  | Karakeep ollama keepalive |
| `KARAKEEP_OLLAMA_URL` |  | Karakeep ollama url |
| `KARAKEEP_OPENAI_KEY` |  | Karakeep openai key |
| `KARAKEEP_OPENAI_URL` |  | Karakeep openai url |
| `KARAKEEP_RESTART` |  | Container restart policy |
| `KARAKEEP_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `KARAKEEP_VERSION` |  | Karakeep version |
| `KARAKEEP_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `./etc/karakeep/data:/data` - Data storage
- `/etc/localtime:/etc/localtime` - Volume mount
- `./etc/karakeep/meilisearch:/meili_data` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${KARAKEEP_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.karakeep.entrypoints=websecure`
- `traefik.http.routers.karakeep.rule=Host(`${KARAKEEP_HOST_NAME:-karakeep}.${HOST_DOMAIN}`)`
- `traefik.http.services.karakeep.loadbalancer.server.port=3000`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${KARAKEEP_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${KARAKEEP_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${KARAKEEP_HOST_NAME:-karakeep}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable karakeep

# Configure environment variables (if needed)
make scaffold karakeep

# Start the service
make up
```

## Notes
- This service consists of 3 containers working together
