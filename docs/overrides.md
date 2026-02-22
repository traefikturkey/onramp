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

Add network storage to services. Configure paths first with `make edit-env-nfs`:

```bash
NFS_SERVER=192.168.1.100
NFS_MEDIA_PATH=/mnt/media
NFS_MOVIES_PATH=${NFS_MEDIA_PATH}/movies
NFS_SHOWS_PATH=${NFS_MEDIA_PATH}/shows
NFS_DOWNLOADS_PATH=${NFS_MEDIA_PATH}/downloads
```

#### Media Servers

| Override | Service | Description |
|----------|---------|-------------|
| `plex-nfs` | Plex | Mount NFS media library |
| `plex-nfs-extra` | Plex | Additional NFS mount paths |
| `jellyfin-nfs` | Jellyfin | Mount NFS media library |

#### Media Management (Arr Stack)

| Override | Service | Description |
|----------|---------|-------------|
| `sonarr-nfs` | Sonarr | Mount NFS for TV shows |
| `sonarr-nfs-extra` | Sonarr | Additional NFS paths for Sonarr |
| `radarr-nfs` | Radarr | Mount NFS for movies |
| `lidarr-nfs` | Lidarr | Mount NFS for music |
| `bazarr-nfs` | Bazarr | Mount NFS for subtitles |
| `kapowarr-nfs` | Kapowarr | Mount NFS for comics |
| `headphones-nfs` | Headphones | Mount NFS for music |
| `lazylibrarian-nfs` | LazyLibrarian | Mount NFS for books |

#### Download Clients

| Override | Service | Description |
|----------|---------|-------------|
| `sabnzbd-nfs` | SABnzbd | Mount NFS downloads directory |
| `nzbget-nfs` | NZBGet | Mount NFS downloads directory |
| `transmission-vpn-nfs` | Transmission (VPN) | Mount NFS downloads via VPN container |
| `pinchflat-nfs` | Pinchflat | Mount NFS for YouTube downloads |
| `youtube-dl-nfs` | youtube-dl | Mount NFS for downloaded videos |

#### Transcoding

| Override | Service | Description |
|----------|---------|-------------|
| `tdarr-nfs` | Tdarr | Mount NFS media library for transcoding |
| `makemkv-nfs` | MakeMKV | Mount NFS for ripped media |
| `unmanic-nfs` | Unmanic | Mount NFS media library |

#### Photos & Books

| Override | Service | Description |
|----------|---------|-------------|
| `immich-nfs` | Immich | Mount NFS photo library |
| `photoprism-nfs` | PhotoPrism | Mount NFS photo library |
| `librephotos-nfs` | LibrePhotos | Mount NFS photo library |
| `lychee-nfs` | Lychee | Mount NFS photo library |
| `audiobookshelf-nfs` | Audiobookshelf | Mount NFS audiobooks |
| `komga-nfs` | Komga | Mount NFS for comics/books |
| `kaizoku-nfs` | Kaizoku | Mount NFS for manga |
| `booklore-nfs` | Booklore | Mount NFS book library |

#### Audio & Podcasts

| Override | Service | Description |
|----------|---------|-------------|
| `navidrome-nfs` | Navidrome | Mount NFS music library |
| `owncast-nfs` | Owncast | Mount NFS for streaming content |

#### Storage & Backup

| Override | Service | Description |
|----------|---------|-------------|
| `nextcloud-nfs` | Nextcloud | Mount NFS user data |
| `syncthing-nfs` | Syncthing | Mount NFS sync directories |
| `minio-nfs` | MinIO | Mount NFS object storage |
| `duplicati-nfs` | Duplicati | Mount NFS backup source |
| `sietch-nfs-backup` | Sietch | Mount NFS for backup destination |
| `samba-nfs` | Samba | Re-export NFS share via SMB |
| `qdirstat-nfs` | QDirStat | Mount NFS for disk usage analysis |
| `ubuntu-nfs` | Ubuntu | Mount NFS in Ubuntu container |

#### Surveillance

| Override | Service | Description |
|----------|---------|-------------|
| `frigate-cpu-nfs` | Frigate | Mount NFS recordings (CPU mode) |
| `frigate-nvidia-nfs` | Frigate | Mount NFS recordings (Nvidia GPU mode) |

#### Productivity & Notes

| Override | Service | Description |
|----------|---------|-------------|
| `obsidian-nfs` | Obsidian | Mount NFS vault |
| `joplin-api-nfs` | Joplin API | Mount NFS notes |
| `trilium-nfs` | Trilium | Mount NFS notes |
| `gitea-nfs` | Gitea | Mount NFS repositories |
| `influxdb-nfs` | InfluxDB | Mount NFS data directory |
| `synapse-nfs` | Synapse | Mount NFS Matrix data |

#### Food & Home

| Override | Service | Description |
|----------|---------|-------------|
| `mealie-nfs` | Mealie | Mount NFS recipe data |
| `grocy-nfs` | Grocy | Mount NFS grocery data |
| `tandoor-nfs` | Tandoor | Mount NFS recipe data |
| `homebox-nfs` | Homebox | Mount NFS inventory data |
| `copyparty-nfs` | Copyparty | Mount NFS file storage |
| `netbootxyz-nfs` | netboot.xyz | Mount NFS for boot assets |
| `wallabag-nfs` | Wallabag | Mount NFS read-later data |
| `firefly3-nfs` | Firefly III | Mount NFS financial data |

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
| `unmanic-quicksync` | Intel | Unmanic |
| `ollama-nvidia` | Nvidia | Ollama |
| `ollama-amd` | AMD | Ollama |

### Dedicated Databases

Run service-specific database containers:

| Override | Database | Service |
|----------|----------|---------|
| `odoo-dedicated-postgres` | PostgreSQL | Odoo |
| `authentik-dedicated-redis` | Redis | Authentik |
| `booklore-dedicated-mariadb` | MariaDB | Booklore |
| `dawarich-dedicated-redis` | Redis | Dawarich |
| `docmost-dedicated-postgres` | PostgreSQL | Docmost |
| `docmost-dedicated-redis` | Redis | Docmost |
| `firefly3-dedicated-mariadb` | MariaDB | Firefly III |
| `healthchecks-postgres` | PostgreSQL | Healthchecks |
| `immich-dedicated-valkey` | Valkey | Immich |
| `itflow-dedicated-mariadb` | MariaDB | ITFlow |
| `joplin-dedicated-postgres` | PostgreSQL | Joplin |
| `kaizoku-dedicated-redis` | Redis | Kaizoku |
| `kaneo-postgres` | PostgreSQL | Kaneo |
| `manyfold-dedicated-postgres` | PostgreSQL | Manyfold |
| `manyfold-dedicated-redis` | Redis | Manyfold |
| `mediamanager-postgres` | PostgreSQL | Media Manager |
| `n8n-postgres` | PostgreSQL | n8n |
| `netbox-dedicated-postgres` | PostgreSQL | NetBox |
| `netbox-dedicated-redis` | Redis | NetBox |
| `newsdash-dedicated-redis` | Redis | Newsdash |
| `paperless-ngx-dedicated-mariadb` | MariaDB | Paperless-ngx |
| `paperless-ngx-dedicated-redis` | Redis | Paperless-ngx |
| `paperless-ngx-postgres-dedicated-redis` | Redis | Paperless-ngx (Postgres) |
| `semaphore-dedicated-mysql` | MySQL | Semaphore |
| `semaphore-pg` | PostgreSQL | Semaphore |
| `spacebin-dedicated-postgres` | PostgreSQL | Spacebin |
| `speedtest-tracker-shared-postgres` | PostgreSQL | Speedtest Tracker |
| `unimus-dedicated-mariadb` | MariaDB | Unimus |
| `vikunja-dedicated-mariadb` | MariaDB | Vikunja |
| `wallabag-dedicated-mariadb` | MariaDB | Wallabag |
| `wallabag-dedicated-redis` | Redis | Wallabag |
| `yamtrack-dedicated-redis` | Redis | Yamtrack |

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
| `bazarr-extra` | Additional Bazarr configuration |
| `joyride-adguard` | AdGuard integration for Joyride |
| `minecraft-dynmap` | Enable Dynmap web map |
| `omada-cert` | Custom certificate for Omada |
| `pihole-admin` | Enable admin interface |
| `prestashop-arm` | ARM architecture support for PrestaShop |
| `promtail-syslog` | Enable syslog input for Promtail |
| `traefik-idrac` | iDRAC proxy via Traefik |
| `traefik-podman-socket` | Podman socket for Traefik |
| `ubuntu-smb` | SMB mount in Ubuntu container |
| `wordpress-upload` | Increase upload limits |

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
