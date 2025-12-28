# Docker Compose Overrides

Overrides extend existing service definitions without modifying the original YAML files. Use them to add NFS mounts, GPU passthrough, or other customizations.

## How It Works

Docker Compose merges multiple YAML files. When you enable an override, it's included alongside the base service definition, and matching keys are merged.

## Directory Structure

```
overrides-available/    # Available override definitions
overrides-enabled/      # Active overrides (symlinked)
```

## Commands

| Command | Description |
|---------|-------------|
| `make list-overrides` | List available overrides |
| `make enable-override NAME` | Enable override |
| `make disable-override NAME` | Disable override |

## Override Types

### NFS Mounts

Add network storage to media services:

| Override | Service | Description |
|----------|---------|-------------|
| `plex-nfs` | Plex | Mount NFS media library |
| `jellyfin-nfs` | Jellyfin | Mount NFS media library |
| `sonarr-nfs` | Sonarr | Mount NFS for TV shows |
| `radarr-nfs` | Radarr | Mount NFS for movies |
| `audiobookshelf-nfs` | Audiobookshelf | Mount NFS audiobooks |

Configuration in `services-enabled/.env.nfs`:
```bash
NFS_MEDIA_SERVER=192.168.1.100
NFS_MEDIA_PATH=/mnt/media
NFS_TV_PATH=/mnt/media/tv
NFS_MOVIES_PATH=/mnt/media/movies
```

### GPU Passthrough

Enable hardware transcoding:

| Override | GPU Type | Service |
|----------|----------|---------|
| `plex-quicksync` | Intel | Plex |
| `plex-nvidia` | Nvidia | Plex |
| `jellyfin-quicksync` | Intel | Jellyfin |
| `jellyfin-nvidia` | Nvidia | Jellyfin |
| `tdarr-quicksync` | Intel | Tdarr |
| `tdarr-nvidia` | Nvidia | Tdarr |
| `ollama-nvidia` | Nvidia | Ollama |
| `ollama-amd` | AMD | Ollama |

### Dedicated Databases

Run service-specific database containers:

| Override | Database | Service |
|----------|----------|---------|
| `odoo-dedicated-postgres` | PostgreSQL | Odoo |
| `authentik-dedicated-redis` | Redis | Authentik |
| `paperless-ngx-dedicated-mariadb` | MariaDB | Paperless-ngx |
| `vikunja-dedicated-mariadb` | MariaDB | Vikunja |

### VPN Integration

Route traffic through VPN:

| Override | VPN | Service |
|----------|-----|---------|
| `transmission-gluetun` | Gluetun | Transmission |
| `sabnzbd-gluetun` | Gluetun | SABnzbd |
| `transmission-vpn-nord` | NordVPN | Transmission |

### Other

| Override | Description |
|----------|-------------|
| `wordpress-upload` | Increase upload limits |
| `pihole-admin` | Enable admin interface |
| `minecraft-dynmap` | Enable Dynmap web map |

## Usage Example

Enable NFS for Plex:

```bash
# 1. Configure NFS paths
make edit-env-nfs

# 2. Enable the override
make enable-override plex-nfs

# 3. Restart to apply
make restart
```

## Creating Custom Overrides

1. Create a YAML file in `overrides-available/`:
   ```yaml
   # overrides-available/myservice-custom.yml
   services:
     myservice:
       volumes:
         - /custom/path:/data
       environment:
         - CUSTOM_VAR=value
   ```

2. Enable it:
   ```bash
   make enable-override myservice-custom
   make restart
   ```

## Override Syntax

Overrides follow Docker Compose merge rules:

- **Arrays** (volumes, ports): Items are appended
- **Maps** (environment, labels): Keys are merged, same keys overwritten
- **Scalars** (image, command): Replaced entirely

Example base service:
```yaml
services:
  myapp:
    volumes:
      - ./data:/data
    environment:
      - VAR1=original
```

Override:
```yaml
services:
  myapp:
    volumes:
      - /nfs/extra:/extra    # Appended
    environment:
      - VAR1=overridden      # Replaced
      - VAR2=new             # Added
```

Result:
```yaml
services:
  myapp:
    volumes:
      - ./data:/data
      - /nfs/extra:/extra
    environment:
      - VAR1=overridden
      - VAR2=new
```

## Troubleshooting

### Override not taking effect

1. Verify it's enabled:
   ```bash
   ls -la overrides-enabled/
   ```

2. Check the merged config:
   ```bash
   docker compose config | grep -A 20 myservice
   ```

3. Restart the service:
   ```bash
   make restart-service myservice
   ```

### Conflicting overrides

Don't enable conflicting GPU overrides (e.g., both `plex-nvidia` and `plex-quicksync`). Only one GPU type can be used at a time.
