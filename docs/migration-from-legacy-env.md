# Migration from Legacy .env (Master Branch)

This document explains the automatic migration process for users upgrading from the legacy OnRamp master branch that used a single monolithic `.env` file.

## Overview

The legacy OnRamp system stored all configuration in a single `.env` file at the project root. The new modular system splits configuration into:

- `services-enabled/.env` - Global configuration (domain, Cloudflare credentials, timezone)
- `services-enabled/<service>.env` - Per-service configuration
- `services-enabled/.env.nfs` - NFS mount settings (optional)
- `services-enabled/.env.external` - External service proxy settings (optional)
- `services-enabled/custom.env` - Unmapped/custom variables

## When Migration Runs

Migration is triggered automatically when:
1. A `.env` file exists in the project root
2. `services-enabled/.env` does NOT exist

The migration runs during `make`, `make build`, or `make install`.

## What Gets Migrated

### Global Variables → `services-enabled/.env`

Core configuration variables are extracted to the global env file:

| Variable | Description |
|----------|-------------|
| `CF_API_EMAIL` | Cloudflare account email |
| `CF_DNS_API_TOKEN` | Cloudflare API token |
| `HOST_NAME` | Server hostname |
| `HOST_DOMAIN` | Domain name |
| `TZ` | Timezone |
| `PUID` / `PGID` | User/Group IDs |
| `DNS_CHALLENGE_*` | DNS challenge settings |
| `TRAEFIK_*` | Traefik configuration |
| `AZURE_*` | Azure DNS settings |
| `ONRAMP_BACKUP_*` | Backup configuration |

### NFS Variables → `services-enabled/.env.nfs`

NFS and SAMBA mount configuration variables:

| Prefix | Description |
|--------|-------------|
| `NFS_*` | NFS server and path settings |
| `SAMBA_*` | SAMBA share settings |

### External Service Variables → `services-enabled/.env.external`

Variables for proxying to external devices/services not managed by OnRamp:

| Prefix | Description |
|--------|-------------|
| `HOMEASSISTANT_*` | Home Assistant proxy |
| `IDRAC_*` | Dell iDRAC proxy |
| `PROXMOX_*` | Proxmox VE proxy |
| `TRUENAS_*` | TrueNAS proxy |
| `SYNOLOGY_*` | Synology NAS proxy |
| `PFSENSE_*` / `OPNSENSE_*` | Firewall proxies |
| `PBS_*` | Proxmox Backup Server |
| `RANCHER_*` | Rancher proxy |
| `PIHOLE_ADDRESS` / `PIHOLE_HOST_NAME` | External Pi-hole proxy |

### Service Variables → `services-enabled/<service>.env`

Variables are automatically categorized by their prefix:

| Prefix | Destination File |
|--------|-----------------|
| `ADGUARD_*` | `adguard.env` |
| `PLEX_*` | `plex.env` |
| `JELLYFIN_*` | `jellyfin.env` |
| `PIHOLE_*` (except ADDRESS/HOST_NAME) | `pihole.env` |
| `NEXTCLOUD_*` | `nextcloud.env` |
| `POSTGRES_*` | `postgres.env` |
| ... | ... |

Over 80 service prefixes are recognized. See `sietch/scripts/migrate-env.py` for the complete list.

### Unmapped Variables → `services-enabled/custom.env`

Any variables that don't match a known global, NFS, external, or service pattern are preserved in `custom.env`. This ensures no configuration is lost during migration.

## Backup Location

Your original `.env` file is backed up to:
```
backups/.env.legacy
```

The backup preserves the exact contents of your original file, including comments.

## Migration Process

1. **Detection**: System detects `.env` exists and `services-enabled/.env` doesn't
2. **Parsing**: All variables are read, preserving comments
3. **Categorization**: Variables sorted into global, NFS, external, service-specific, or custom buckets
4. **Writing**: New modular files created with migration headers
5. **Backup**: Original `.env` copied to `backups/.env.legacy`
6. **Cleanup**: Original `.env` removed

## Preview Migration (Dry Run)

To see what migration would do without making changes:

```bash
make migrate-env-dry-run
```

This shows:
- Which variables would go to global config (`.env`)
- Which variables would go to NFS config (`.env.nfs`)
- Which variables would go to external config (`.env.external`)
- Which variables would go to each service file
- Which variables would go to custom.env

## Force Re-Migration

If you need to re-run migration (e.g., after restoring from backup):

```bash
make migrate-env-force
```

This removes `services-enabled/.env` and runs migration again.

## Post-Migration

After migration completes:

1. **Verify global config**: `make edit-env-onramp`
2. **Check NFS config**: `make edit-env-nfs`
3. **Check external services**: `make edit-env-external`
4. **Check service configs**: `make edit-env <service>`
5. **Review custom variables**: `make edit-env-custom`
6. **Test your setup**: `make start-staging`

## Example Migration

### Before (Legacy `.env`)
```bash
# Cloudflare settings
CF_API_EMAIL=user@example.com
CF_DNS_API_TOKEN=abc123
HOST_NAME=server
HOST_DOMAIN=example.com
TZ=US/Eastern

# NFS settings
NFS_SERVER=nfs.example.com
NFS_MEDIA_PATH=/mnt/media

# External services
PROXMOX_ADDRESS=192.168.1.100
PROXMOX_HOST_NAME=pve

# Plex settings
PLEX_CLAIM=claim-xxxxx
PLEX_MEDIA_VOLUME=/media

# Pihole settings
PIHOLE_WEBPASSWORD=secret123

# Custom setting
MY_CUSTOM_VAR=value
```

### After Migration

**`services-enabled/.env`**
```bash
# OnRamp Global Configuration
# Migrated from legacy .env on 2024-01-15 10:30:00

CF_API_EMAIL=user@example.com
CF_DNS_API_TOKEN=abc123
HOST_NAME=server
HOST_DOMAIN=example.com
TZ=US/Eastern
```

**`services-enabled/.env.nfs`**
```bash
# NFS/SAMBA Configuration
# Migrated from legacy .env on 2024-01-15 10:30:00

NFS_SERVER=nfs.example.com
NFS_MEDIA_PATH=/mnt/media
```

**`services-enabled/.env.external`**
```bash
# External Service Proxying
# Migrated from legacy .env on 2024-01-15 10:30:00

PROXMOX_ADDRESS=192.168.1.100
PROXMOX_HOST_NAME=pve
```

**`services-enabled/plex.env`**
```bash
# PLEX Configuration
# Migrated from legacy .env on 2024-01-15 10:30:00

PLEX_CLAIM=claim-xxxxx
PLEX_MEDIA_VOLUME=/media
```

**`services-enabled/pihole.env`**
```bash
# PIHOLE Configuration
# Migrated from legacy .env on 2024-01-15 10:30:00

PIHOLE_WEBPASSWORD=secret123
```

**`services-enabled/custom.env`**
```bash
# Custom/Unmapped Variables
# Migrated from legacy .env on 2024-01-15 10:30:00

MY_CUSTOM_VAR=value
```

## Troubleshooting

### Migration didn't run
- Check that `.env` exists in project root
- Check that `services-enabled/.env` doesn't already exist
- Run `make migrate-env-dry-run` to verify detection

### Variables in wrong file
- Edit the destination file directly: `make edit-env <service>`
- Or move variables manually between files
- The system loads all `.env` files, so functionality isn't affected

### Need to restore original
```bash
cp backups/.env.legacy .env
rm services-enabled/.env
make migrate-env-dry-run  # Preview again
```

### Custom variables not recognized
- They're preserved in `services-enabled/custom.env`
- You can move them to appropriate service files manually
- Or leave them in custom.env - they'll still be loaded

## Related Documentation

- [Migration from Feature Branch](migration-from-feature-branch.md)
- [Environment Variables](../README.md#environment-variables)
