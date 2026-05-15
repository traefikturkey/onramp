# Vault

> A tool for secrets management, encryption as a service, and privileged access management

## Links
- [Official Repository](https://github.com/hashicorp/vault)
- [Official Documentation](https://developer.hashicorp.com/vault)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/vault.yml)

## Docker Images
- `hashicorp/vault:${VAULT_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |
| `VAULT_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `VAULT_CONTAINER_NAME` |  | Container name |
| `VAULT_DEFAULT_LEASE_TTL` |  | Vault default lease ttl |
| `VAULT_DOCKER_TAG` |  | Docker image tag/version |
| `VAULT_HOST_NAME` |  | Vault host name |
| `VAULT_MAX_LEASE_TTL` |  | Vault max lease ttl |
| `VAULT_MEM_LIMIT` |  | Vault mem limit |
| `VAULT_RESTART` |  | Container restart policy |
| `VAULT_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `VAULT_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |

## Configuration

### Volumes
- `./etc/vault/logs:/vault/logs` - Volume mount
- `./etc/vault/file:/vault/file` - Volume mount
- `./etc/vault/config:/vault/config` - Configuration files
- `/etc/localtime:/etc/localtime` - Volume mount

### Networks
- `traefik`

### Labels
**Traefik Configuration:**
- `traefik.enable=${VAULT_TRAEFIK_ENABLED:-true}`
- `traefik.http.routers.vault.entrypoints=websecure`
- `traefik.http.routers.vault.rule=Host(`${VAULT_HOST_NAME:-vault}.${HOST_DOMAIN}`)`
- `traefik.http.services.vault.loadbalancer.server.port=8200`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${VAULT_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${VAULT_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${VAULT_HOST_NAME:-vault}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable vault

# Configure environment variables (if needed)
make scaffold vault

# Start the service
make up
```
