# Migration from Feature Branch (onramp-rework-env)

This document explains the automatic migration process for users upgrading from the `onramp-rework-env` feature branch to the new unified environment system.

## Overview

The feature branch used a different environment structure:

**Feature Branch Structure:**
```
environments-available/          # Template files (100+ services)
├── onramp.template
├── onramp-external.template
├── onramp-nfs.template
├── postgres.template
├── nextcloud.template
└── ...

environments-enabled/            # Generated .env files
├── onramp.env
├── onramp-external.env
├── onramp-nfs.env
├── postgres.env
└── ...
```

**New Structure:**
```
services-enabled/               # All env files in one location
├── .env                        # Global config (from onramp.env)
├── .env.external               # External services (from onramp-external.env)
├── .env.nfs                    # NFS config (from onramp-nfs.env)
├── postgres.env                # Service configs (direct copy)
└── ...

services-scaffold/              # Templates (replaces environments-available/)
├── onramp/
│   └── .env.template
├── adguard/
│   └── env.template
└── ...
```

## When Migration Runs

Migration is triggered automatically when either:
1. `environments-enabled/` directory exists with `.env` files
2. `environments-available/` directory exists with `.template` files

AND `services-enabled/.env` does NOT exist.

The migration runs during `make`, `make build`, or `make install`.

## What Gets Migrated

### File Mapping

| Source (Feature Branch) | Destination (New System) |
|------------------------|-------------------------|
| `environments-enabled/onramp.env` | `services-enabled/.env` |
| `environments-enabled/onramp-external.env` | `services-enabled/.env.external` |
| `environments-enabled/onramp-nfs.env` | `services-enabled/.env.nfs` |
| `environments-enabled/<service>.env` | `services-enabled/<service>.env` |

### Variable Names

**No variable renaming occurs.** The feature branch already uses standard variable names in the generated `.env` files:

- `CF_API_EMAIL` (not `ONRAMP_CF_API_EMAIL`)
- `HOST_NAME` (not `ONRAMP_HOST_NAME`)
- `POSTGRES_PASS`, `PIHOLE_WEBPASSWORD`, etc.

The `ONRAMP_` prefix only existed in the `.template` files, not in the generated output.

## What Gets Cleaned Up

After migration, the following directories are removed:

| Directory | Backup Location | Reason |
|-----------|----------------|--------|
| `environments-enabled/` | `backups/environments-enabled.legacy/` | Replaced by `services-enabled/` |
| `environments-available/` | `backups/environments-available.legacy/` | Replaced by `services-scaffold/` |

## Migration Scenarios

### Scenario 1: Full Feature Branch Setup
User has both templates and generated env files.

**What happens:**
1. All `.env` files migrated to `services-enabled/`
2. `environments-enabled/` backed up and removed
3. `environments-available/` backed up and removed

### Scenario 2: Partial Setup (Templates Only)
User cloned feature branch but never ran `make` to generate env files.

**What happens:**
1. No env files to migrate
2. `environments-available/` backed up and removed
3. User proceeds with fresh setup using `services-scaffold/`

### Scenario 3: Partial Cleanup
User has env files but templates were already removed.

**What happens:**
1. All `.env` files migrated to `services-enabled/`
2. `environments-enabled/` backed up and removed

## Backup Locations

All original files are preserved:

```
backups/
├── environments-enabled.legacy/    # Your generated env files
│   ├── onramp.env
│   ├── postgres.env
│   └── ...
└── environments-available.legacy/  # Template files
    ├── onramp.template
    ├── postgres.template
    └── ...
```

## Preview Migration (Dry Run)

To see what migration would do without making changes:

```bash
make migrate-env-dry-run
```

Output shows:
- Number of environment files to migrate
- Source → destination mapping for each file
- Number of template files to clean up

## Force Re-Migration

If you need to re-run migration:

```bash
make migrate-env-force
```

This removes `services-enabled/.env` and runs migration again.

## Post-Migration

After migration completes:

1. **Verify global config**: `make edit-env-onramp`
2. **Check external services**: `make edit-env-external`
3. **Check NFS config**: `make edit-env-nfs`
4. **Check service configs**: `make edit-env <service>`
5. **Test your setup**: `make start-staging`

## Example Migration

### Before (Feature Branch)

**`environments-enabled/onramp.env`**
```bash
###############################################
# ONRAMP settings
###############################################
CF_API_EMAIL=user@example.com
CF_DNS_API_TOKEN=abc123
HOST_NAME=server
HOST_DOMAIN=example.com
TZ=US/Eastern
```

**`environments-enabled/postgres.env`**
```bash
###############################################
# POSTGRES settings
###############################################
POSTGRES_PASS=secretpassword
POSTGRES_USER=admin
POSTGRES_DB=mydb
```

### After Migration

**`services-enabled/.env`**
```bash
# OnRamp Configuration
# Migrated from feature branch on 2024-01-15 10:30:00
# Original: onramp.env

###############################################
# ONRAMP settings
###############################################
CF_API_EMAIL=user@example.com
CF_DNS_API_TOKEN=abc123
HOST_NAME=server
HOST_DOMAIN=example.com
TZ=US/Eastern
```

**`services-enabled/postgres.env`**
```bash
# OnRamp Configuration
# Migrated from feature branch on 2024-01-15 10:30:00
# Original: postgres.env

###############################################
# POSTGRES settings
###############################################
POSTGRES_PASS=secretpassword
POSTGRES_USER=admin
POSTGRES_DB=mydb
```

## Key Differences from Legacy Migration

| Aspect | Legacy (.env) Migration | Feature Branch Migration |
|--------|------------------------|-------------------------|
| Source | Single `.env` file | Multiple `environments-enabled/*.env` files |
| Processing | Parse and categorize by prefix | Direct file copy with rename |
| Variable changes | None | None |
| Templates cleanup | N/A | Removes `environments-available/` |
| Custom vars | Go to `custom.env` | N/A (files already organized) |

## Troubleshooting

### Migration didn't run
- Check for `environments-enabled/` OR `environments-available/` directories
- Check that `services-enabled/.env` doesn't already exist
- Run `make migrate-env-dry-run` to verify detection

### Missing service config after migration
- Check `backups/environments-enabled.legacy/` for the original file
- Copy it manually: `cp backups/environments-enabled.legacy/<service>.env services-enabled/`

### Need to restore original structure
```bash
# Restore env files
cp -r backups/environments-enabled.legacy environments-enabled

# Restore templates (if needed)
cp -r backups/environments-available.legacy environments-available

# Remove new structure
rm -rf services-enabled/.env services-enabled/*.env

# Run dry-run to verify
make migrate-env-dry-run
```

### Templates directory wasn't cleaned up
- Check if `environments-available/` still exists
- If so, back it up manually and remove it
- The new system uses `services-scaffold/` instead

## New Workflow After Migration

### Enabling a Service
```bash
# Old (feature branch):
# - Would run env-subst.py to prompt for variables
# - Created file in environments-enabled/

# New:
make enable-service postgres
# - Creates symlink in services-enabled/
# - Scaffolds config from services-scaffold/ if available
# - Creates services-enabled/postgres.env
```

### Editing Configuration
```bash
# Old: make edit-env postgres → environments-enabled/postgres.env
# New: make edit-env postgres → services-enabled/postgres.env

make edit-env-onramp     # Global config
make edit-env postgres   # Service config
make edit-env-nfs        # NFS config
make edit-env-external   # External services
```

## Related Documentation

- [Migration from Legacy .env](migration-from-legacy-env.md)
- [Environment Variables](../README.md#environment-variables)
