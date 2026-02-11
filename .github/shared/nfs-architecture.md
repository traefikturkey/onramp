# NFS Architecture

OnRamp uses NFS (Network File System) to mount remote storage into service containers. NFS support is implemented through the override pattern, keeping it optional and separate from core service definitions.

## Core Concepts

### The Override Pattern

NFS mounts are not defined in main service YAML files (`services-available/*.yml`). Instead, each service that supports NFS has a dedicated override file:

```
overrides-available/<service>-nfs.yml    # NFS override definition
overrides-enabled/<service>-nfs.yml      # Symlink = NFS active for this service
```

This keeps NFS optional. Services work with local storage by default and gain NFS support only when the override is explicitly enabled.

### Global NFS Configuration

NFS infrastructure settings live in a single global file:

```
services-scaffold/onramp/.env.nfs.template  →  services-enabled/.env.nfs
```

This template generates the user's `.env.nfs` file and contains **shared infrastructure variables** used across many services. Users edit their NFS settings with:

```bash
make edit-env-nfs
```

## Variable Naming Convention

NFS overrides use a two-tier variable pattern that provides per-service customization with sensible shared defaults.

### NFS Server Address

```yaml
o: "addr=${SERVICE_NFS_SERVER:-${NFS_SERVER}},nolock,noatime,soft,rw"
```

| Variable | Purpose | Scope |
|----------|---------|-------|
| `SERVICE_NFS_SERVER` | Per-service NFS server override | Service-specific |
| `NFS_SERVER` | Global NFS server fallback | Shared (in `.env.nfs`) |

Most users have a single NFS server, so `NFS_SERVER` is sufficient. The per-service override exists for multi-server setups.

### NFS Share Path

```yaml
device: ":${SERVICE_NFS_SERVER_PATH:-${NFS_SHARED_CATEGORY_PATH}}"
```

| Variable | Purpose | Scope |
|----------|---------|-------|
| `SERVICE_NFS_SERVER_PATH` | Per-service path override | Service-specific |
| `NFS_SHARED_CATEGORY_PATH` | Shared category fallback | Shared category |

The fallback is always a **shared category path** — a path that multiple services logically share. These category paths are:

| Category Variable | Used By | In Global Template? |
|-------------------|---------|---------------------|
| `NFS_MEDIA_PATH` | plex, jellyfin, tdarr, samba, gitea, qdirstat, pinchflat | Yes |
| `NFS_DOWNLOADS_PATH` | sonarr, radarr, transmission, sabnzbd, nzbget, tdarr | Yes |
| `NFS_MOVIES_PATH` | radarr, bazarr | No (implicit) |
| `NFS_SHOWS_PATH` | sonarr, bazarr | No (implicit) |
| `NFS_MUSIC_PATH` | lidarr | No (implicit) |
| `NFS_BOOKS_PATH` | audiobookshelf | No (implicit) |
| `NFS_PODCASTS_PATH` | audiobookshelf | No (implicit) |
| `NFS_BACKUP_PATH` | duplicati, sietch-nfs-backup | Yes |

Category paths that serve shared infrastructure (like `NFS_BACKUP_PATH`) are defined in the global template. Category paths that are content-type-specific (like `NFS_BOOKS_PATH`) are set by users in their local `.env.nfs` as needed.

### Real Examples

**Plex** (`overrides-available/plex-nfs.yml`) — falls back to shared media path:

```yaml
volumes:
  plex-nfs-media:
    driver_opts:
      type: nfs
      o: "addr=${PLEX_MEDIA_NFS_SERVER:-${NFS_SERVER}},nolock,noatime,soft,rw"
      device: ":${PLEX_MEDIA_NFS_SERVER_PATH:-${NFS_MEDIA_PATH}}"
```

**Sonarr** (`overrides-available/sonarr-nfs.yml`) — two volumes, each with shared category fallback:

```yaml
volumes:
  sonarr-nfs-media:
    driver_opts:
      type: nfs
      o: "addr=${SONARR_MEDIA_NFS_SERVER:-${NFS_SERVER}},nolock,noatime,soft,rw"
      device: ":${SONARR_MEDIA_NFS_SERVER_PATH:-${NFS_SHOWS_PATH}}"

  sonarr-nfs-downloads:
    driver_opts:
      type: nfs
      o: "addr=${SONARR_MEDIA_NFS_SERVER:-${NFS_SERVER}},nolock,noatime,soft,rw"
      device: ":${SONARR_MEDIA_NFS_DOWNLOADS_PATH:-${NFS_DOWNLOADS_PATH}}"
```

**Duplicati** (`overrides-available/duplicati-nfs.yml`) — falls back to shared backup path:

```yaml
volumes:
  duplicati-nfs-backup:
    driver_opts:
      type: nfs
      o: "addr=${DUPLICATI_BACKUP_NFS_SERVER:-${NFS_SERVER}},nolock,noatime,soft,rw"
      device: ":${DUPLICATI_BACKUP_NFS_SERVER_PATH:-${NFS_BACKUP_PATH}}"
```

## How to Add NFS Support to a New Service

### Step 1: Choose the Shared Category

Determine which shared NFS path your service logically falls under:

- Media content (video, photos, etc.) → `NFS_MEDIA_PATH`
- Downloads → `NFS_DOWNLOADS_PATH`
- Backups → `NFS_BACKUP_PATH`
- Subcategory (movies, shows, music, books) → `NFS_MOVIES_PATH`, `NFS_SHOWS_PATH`, etc.

If none of the existing categories fit, use the closest match. Users who need a different path can always override with the service-specific variable.

### Step 2: Create the Override File

Create `overrides-available/<service>-nfs.yml`:

```yaml
volumes:
  <service>-nfs-<purpose>:
    labels:
      - remove_volume_on=down
    driver_opts:
      type: nfs
      o: "addr=${<SERVICE>_<PURPOSE>_NFS_SERVER:-${NFS_SERVER}},nolock,noatime,soft,rw"
      device: ":${<SERVICE>_<PURPOSE>_NFS_SERVER_PATH:-${NFS_SHARED_CATEGORY_PATH}}"

services:
  <service>:
    volumes:
      - ${<SERVICE>_CONFIG_VOLUME:-./etc/<service>}:/config
      - ${<SERVICE>_<PURPOSE>_VOLUME:-<service>-nfs-<purpose>}:${<SERVICE>_<PURPOSE>_PATH:-/<mountpoint>}
```

Key requirements:

- **Volume label**: Include `remove_volume_on=down` so NFS volumes are cleaned up when services stop
- **Server variable**: `${SERVICE_PURPOSE_NFS_SERVER:-${NFS_SERVER}}` — always fall back to global
- **Path variable**: `${SERVICE_PURPOSE_NFS_SERVER_PATH:-${NFS_SHARED_CATEGORY}}` — always fall back to a shared category
- **Service volume**: Use a variable with the NFS volume name as default so users can swap to local storage
- **Comment**: Add any service-specific notes (e.g., performance warnings for config-on-NFS)

### Step 3: Test

```bash
# Symlink override
ln -s ../overrides-available/<service>-nfs.yml overrides-enabled/

# Validate YAML
make check-yaml

# Start service
make start-service <service>
```

## How to Enable NFS for a Service

### Prerequisites

1. An NFS server with exported shares
2. The service already enabled (`make enable-service <service>`)

### Steps

1. **Set the global NFS server** (if not already done):

   ```bash
   make edit-env-nfs
   # Set: NFS_SERVER=192.168.1.100
   ```

2. **Enable the NFS override**:

   ```bash
   ln -s ../overrides-available/<service>-nfs.yml overrides-enabled/
   ```

3. **(Optional) Set service-specific path**:

   If your NFS share path differs from the shared default, set it in `.env.nfs`:

   ```bash
   make edit-env-nfs
   # Add: PLEX_MEDIA_NFS_SERVER_PATH=/volume1/media
   ```

4. **Restart the service**:

   ```bash
   make restart-service <service>
   ```

## Global Template Rules

The global `.env.nfs.template` (`services-scaffold/onramp/.env.nfs.template`) defines variables that are generated into every user's `services-enabled/.env.nfs`.

### What Belongs in the Global Template

Shared infrastructure variables used by multiple services or the system itself:

| Variable | Purpose |
|----------|---------|
| `NFS_SERVER` | NFS server address (used by all NFS overrides) |
| `NFS_MEDIA_PATH` | Media share mount point |
| `NFS_DOWNLOADS_PATH` | Downloads share mount point |
| `NFS_MOUNT_OPTIONS` | Default mount options |
| `NFS_BACKUP_PATH` | Backup path (used by backup tooling) |

### What Does NOT Belong in the Global Template

Service-specific path variables that are only used by a single service:

| Variable | Why Not |
|----------|---------|
| `NFS_NEXTCLOUD_PATH` | Used only by nextcloud — set via `NEXTCLOUD_NFS_SERVER_PATH` |
| `NFS_PLEX_PATH` | Used only by plex — set via `PLEX_MEDIA_NFS_SERVER_PATH` |
| `NFS_BOOKS_PATH` | Used only by audiobookshelf — set via `AUDIOBOOKSHELF_MEDIA_NFS_SERVER_PATH` |

If a user needs a custom path for a specific service, they set the service-specific override variable (`SERVICE_NFS_SERVER_PATH`) directly in their local `.env.nfs` file.

## Anti-Patterns

### Adding service-specific paths to the global template

**Wrong:**
```bash
# In .env.nfs.template
NFS_NEXTCLOUD_PATH=/mnt/nextcloud
```

**Right:** The service override falls back to a shared category path. Users who need a custom path set `NEXTCLOUD_NFS_SERVER_PATH` in their local `.env.nfs`.

### Hardcoding site-specific paths in templates

**Wrong:**
```bash
# In .env.nfs.template
NFS_NEXTCLOUD_PATH=/mnt/smtank/Nextcloud   # References a specific ZFS pool
```

**Right:** Templates use generic paths like `/mnt/media`, `/mnt/downloads`, `/mnt/backups`. Site-specific paths go in the user's local `.env.nfs` file (which is not tracked by git).

### Copy-pasting override files without updating comments

**Wrong:**
```yaml
# In nextcloud-nfs.yml
# you should not put plex config directory on nfs, there are serious performance issues
```

**Right:** Update comments to reference the correct service. Review all copy-pasted content for accuracy.

### Using a service-specific path as the fallback instead of a shared category

**Wrong:**
```yaml
device: ":${NEXTCLOUD_NFS_SERVER_PATH:-${NFS_NEXTCLOUD_PATH}}"
#                                       ^^^^^^^^^^^^^^^^^^^^^^^^^
#                      Falls back to a service-specific variable
```

**Right:**
```yaml
device: ":${NEXTCLOUD_NFS_SERVER_PATH:-${NFS_MEDIA_PATH}}"
#                                       ^^^^^^^^^^^^^^^^
#                      Falls back to a shared category
```

## Troubleshooting

### NFS Mount Fails on Service Start

1. Verify `NFS_SERVER` is set: `grep NFS_SERVER services-enabled/.env.nfs`
2. Test NFS connectivity: `showmount -e <nfs-server-ip>`
3. Check the export path exists on the server
4. Verify NFS client packages are installed on the Docker host

### Service Uses Local Storage Instead of NFS

1. Verify the override symlink exists: `ls -la overrides-enabled/<service>-nfs.yml`
2. Restart the service: `make restart-service <service>`
3. Check the volume is created: `docker volume ls | grep nfs`

### Custom Path Not Taking Effect

The variable precedence is:
1. `SERVICE_NFS_SERVER_PATH` (service-specific override) — checked first
2. `NFS_SHARED_CATEGORY_PATH` (shared category fallback) — used if #1 is unset

Set the service-specific variable in `services-enabled/.env.nfs`:
```bash
make edit-env-nfs
# Add: MYSERVICE_NFS_SERVER_PATH=/custom/path
```
