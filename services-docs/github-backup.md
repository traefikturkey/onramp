# Github Backup

> Runs GitHub Backup to periodically archive GitHub repositories and releases

## Links
- [Official Repository](https://github.com/SierraSoftworks/github-backup)
- [Service Configuration](https://github.com/traefikturkey/onramp/tree/main/services-available/github-backup.yml)

## Docker Images
- `${GITHUB_BACKUP_IMAGE:-ghcr.io/sierrasoftworks/github-backup}:${GITHUB_BACKUP_DOCKER_TAG:-latest}`

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `GITHUB_BACKUP_AUTOHEAL_ENABLED` |  | Enable Autoheal container restart on unhealthy status |
| `GITHUB_BACKUP_BACKUPS` |  | Github backup backups |
| `GITHUB_BACKUP_CONFIG` |  | Github backup config |
| `GITHUB_BACKUP_CONTAINER_NAME` |  | Container name |
| `GITHUB_BACKUP_DOCKER_TAG` |  | Docker image tag/version |
| `GITHUB_BACKUP_IMAGE` |  | Github backup image |
| `GITHUB_BACKUP_MEM_LIMIT` |  | Github backup mem limit |
| `GITHUB_BACKUP_RESTART_POLICY` |  | Container restart policy |
| `GITHUB_BACKUP_TRAEFIK_ENABLED` |  | Enable Traefik reverse proxy |
| `GITHUB_BACKUP_WATCHTOWER_ENABLED` |  | Enable Watchtower auto-updates |
| `GITHUB_PERSONAL_ACCESS_TOKEN` |  | Github personal access token |
| `HOST_DOMAIN` |  | Host domain for service access |
| `PGID` |  | Group ID for file permissions |
| `PUID` |  | User ID for file permissions |
| `TZ` |  | Timezone setting |

## Configuration

### Volumes
- `${GITHUB_BACKUP_CONFIG:-./etc/github-backup/config.yaml}` - Configuration files
- `${GITHUB_BACKUP_BACKUPS:-./etc/github-backup/backups}` - Volume mount
- `/etc/localtime:/etc/localtime` - Volume mount

### Labels
**Traefik Configuration:**
- `traefik.enable=${GITHUB_BACKUP_TRAEFIK_ENABLED:-false}`

**Watchtower Configuration:**
- `com.centurylinklabs.watchtower.enable=${GITHUB_BACKUP_WATCHTOWER_ENABLED:-true}`

**Other Labels:**
- `autoheal=${GITHUB_BACKUP_AUTOHEAL_ENABLED:-true}`
- `joyride.host.name=${GITHUB_BACKUP_CONTAINER_NAME:-github-backup}.${HOST_DOMAIN}`

## Quick Start

```bash
# Enable the service
make enable github-backup

# Configure environment variables (if needed)
make scaffold github-backup

# Start the service
make up
```
