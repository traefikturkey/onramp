# Openbrain

> Typed-table memory layer for AI agents (MCP server + dedicated pgvector)

## Links
- [Official Repository](https://github.com/NateBJones-Projects/OB1)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/openbrain.yml)

## Docker Images
- `ghcr.io/crack-kitty/openbrain-mcp:${OPENBRAIN_IMAGE_TAG:-latest}`
- `pgvector/pgvector:${OPENBRAIN_PGVECTOR_TAG:-pg16}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `OPENBRAIN_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `OPENBRAIN_BODY_MAX_WORDS` | 400 | Openbrain body max words |
| `OPENBRAIN_BOOT_BLOCKER_CAP` | 5 | Openbrain boot blocker cap |
| `OPENBRAIN_BOOT_PATTERN_CAP` | 5 | Openbrain boot pattern cap |
| `OPENBRAIN_BOOT_TASK_CAP` | 20 | Openbrain boot task cap |
| `OPENBRAIN_BOOT_TOKEN_CAP` | 2000 | Openbrain boot token cap |
| `OPENBRAIN_CONSOLIDATION_INTERVAL` | 0 | Openbrain consolidation interval |
| `OPENBRAIN_CONTAINER_NAME` | openbrain | Container name |
| `OPENBRAIN_DB_AUTOHEAL_ENABLED` | true | Enable Autoheal container restart on unhealthy status |
| `OPENBRAIN_DB_CONTAINER_NAME` | openbrain-db | Container name |
| `OPENBRAIN_DB_HOST` | openbrain-db | Openbrain db host |
| `OPENBRAIN_DB_NAME` | openbrain | Openbrain db name |
| `OPENBRAIN_DB_PASSWORD` | ${OPENBRAIN_DB_PASSWORD} | Service password |
| `OPENBRAIN_DB_PORT` | 5432 | Service port number |
| `OPENBRAIN_DB_USER` | openbrain | Service username |
| `OPENBRAIN_DB_WATCHTOWER_ENABLED` | false | Enable Watchtower auto-updates |
| `OPENBRAIN_DECAY_LAMBDA` | 0.005 | Openbrain decay lambda |
| `OPENBRAIN_DEDUP_THRESHOLD` | 0.92 | Openbrain dedup threshold |
| `OPENBRAIN_EMBEDDING_DIMENSIONS` | 768 | Openbrain embedding dimensions |
| `OPENBRAIN_EMBEDDING_MODEL` | nomic-embed-text | Openbrain embedding model |
| `OPENBRAIN_EMBEDDING_PROVIDER` | ollama | Openbrain embedding provider |
| `OPENBRAIN_HEADLINE_MAX_WORDS` | 15 | Openbrain headline max words |
| `OPENBRAIN_HOST_NAME` | openbrain | Openbrain host name |
| `OPENBRAIN_HYBRID_WEIGHT` | 0.3 | Openbrain hybrid weight |
| `OPENBRAIN_IMAGE_TAG` | latest | Openbrain image tag |
| `OPENBRAIN_MCP_ACCESS_KEY` | ${OPENBRAIN_MCP_ACCESS_KEY} | Openbrain mcp access key |
| `OPENBRAIN_MERGE_LOWER_THRESHOLD` | 0.70 | Openbrain merge lower threshold |
| `OPENBRAIN_METADATA_LLM_MODEL` | qwen2.5-coder:14b | Openbrain metadata llm model |
| `OPENBRAIN_METADATA_LLM_PROVIDER` | ollama | Openbrain metadata llm provider |
| `OPENBRAIN_OLLAMA_BASE_URL` | http://ollama:11434 | Openbrain ollama base url |
| `OPENBRAIN_OPENAI_API_KEY` | ${OPENBRAIN_OPENAI_API_KEY:-} | Openbrain openai api key |
| `OPENBRAIN_OPENAI_MODEL` | text-embedding-3-small | Openbrain openai model |
| `OPENBRAIN_OPENROUTER_API_KEY` | ${OPENBRAIN_OPENROUTER_API_KEY:-} | Openbrain openrouter api key |
| `OPENBRAIN_PGVECTOR_TAG` | pg16 | Openbrain pgvector tag |
| `OPENBRAIN_RESTART` | unless-stopped | Container restart policy |
| `OPENBRAIN_TRAEFIK_ENABLED` | true | Enable Traefik reverse proxy |
| `OPENBRAIN_WATCHTOWER_ENABLED` | true | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `/apps/onramp/etc/openbrain/pgdata:/var/lib/postgresql/data` - Data storage

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${OPENBRAIN_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.openbrain.entrypoints=websecure`
- `traefik.http.routers.openbrain.rule=Host(`${OPENBRAIN_HOST_NAME:-openbrain}.${HOST_DOMAIN}`)`
- `traefik.http.services.openbrain.loadbalancer.server.port=8080`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${OPENBRAIN_DB_WATCHTOWER_ENABLED:-false}`

**Other Labels:**
- `autoheal=${OPENBRAIN_DB_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${OPENBRAIN_HOST_NAME:-openbrain}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable openbrain

# Configure environment variables (if needed)
make scaffold openbrain

# Start the service
make up
```

## Notes
- This service consists of 2 containers working together
