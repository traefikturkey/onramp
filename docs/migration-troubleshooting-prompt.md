# OnRamp Migration Troubleshooting - Context Prompt

Use this prompt to provide context to an AI assistant when troubleshooting migration issues from the legacy master branch to the new main branch.

---

## Copy everything below this line to provide context:

---

# OnRamp Migration Context for Troubleshooting

I'm working with **OnRamp**, a Docker Compose-based self-hosted homelab project. The project recently underwent a major restructuring:

- **Old system (master branch)**: Single monolithic `.env` file at project root
- **New system (main branch)**: Modular environment files in `services-enabled/` directory

## What Changed

### Directory Structure

**Before (master branch):**
```
.env                      # All config in one file
.templates/               # Legacy shell-script-based scaffolding
services-available/       # Service compose files
```

**After (main branch):**
```
services-enabled/         # All env files now here
├── .env                  # Global config (CF_API_EMAIL, HOST_DOMAIN, TZ, etc.)
├── .env.nfs              # NFS mount settings (optional)
├── .env.external         # External service proxy settings (optional)
├── <service>.env         # Per-service config
└── custom.env            # Unmapped variables

services-scaffold/        # Convention-based templates (replaces .templates/)
├── onramp/
│   └── .env.template
├── adguard/
│   ├── env.template
│   └── AdGuardHome.yaml.template
└── ...

sietch/                   # Python tool container
└── scripts/
    ├── migrate-env.py    # Migration script
    ├── scaffold.py       # Template rendering
    └── ...
```

### Key Files

1. **`sietch/scripts/migrate-env.py`** - Handles automatic migration:
   - Detects if legacy `.env` exists → runs legacy migration
   - Detects if `environments-enabled/` exists → runs feature branch migration
   - Categorizes variables into: global, NFS, external, service-specific, custom
   - Backs up original files to `backups/` before modifying

2. **`make.d/install.mk`** - Build process integration:
   - `ensure-env` target creates `services-enabled/.env` if missing
   - `build` target runs migration automatically

3. **`make.d/sietch.mk`** - Migration make targets:
   - `make migrate-env-dry-run` - Preview migration without changes
   - `make migrate-env-force` - Re-run migration (removes existing services-enabled/.env first)

## Migration Detection Logic

From `migrate-env.py`:

```python
def should_migrate_legacy(self) -> bool:
    """Legacy master branch: .env exists AND services-enabled/.env missing"""
    return self.legacy_env.exists() and not (self.services_enabled / ".env").exists()

def should_migrate_feature_branch(self) -> bool:
    """Feature branch: environments-enabled/ OR environments-available/ exists"""
    has_templates = (
        self.environments_available.exists()
        and any(self.environments_available.glob("*.template"))
    )
    has_env_files = (
        self.environments_enabled.exists()
        and any(self.environments_enabled.glob("*.env"))
    )
    return (has_templates or has_env_files) and not (self.services_enabled / ".env").exists()
```

## Variable Categorization (Legacy Migration)

The script categorizes variables by prefix:

**Global (→ services-enabled/.env):**
- `CF_API_EMAIL`, `CF_DNS_API_TOKEN`, `HOST_NAME`, `HOST_DOMAIN`, `TZ`, `PUID`, `PGID`
- `TRAEFIK_*`, `DNS_CHALLENGE_*`, `AZURE_*`, `ONRAMP_BACKUP_*`

**NFS (→ services-enabled/.env.nfs):**
- Variables starting with `NFS_` or `SAMBA_`

**External Services (→ services-enabled/.env.external):**
- `HOMEASSISTANT_*`, `PROXMOX_*`, `TRUENAS_*`, `SYNOLOGY_*`, `PFSENSE_*`, etc.
- Special: `PIHOLE_ADDRESS`, `PIHOLE_HOST_NAME` (external pihole proxy)

**Service-specific (→ services-enabled/<service>.env):**
- Variables matched by prefix (e.g., `PLEX_*` → `plex.env`, `POSTGRES_*` → `postgres.env`)
- 80+ service prefixes recognized

**Custom (→ services-enabled/custom.env):**
- Any unrecognized variables

## Common Issues

### 1. Migration Not Running
- **Symptom**: No files appear in `services-enabled/`
- **Check**: Does `.env` exist at root? Does `services-enabled/.env` already exist?
- **Debug**: `make migrate-env-dry-run`

### 2. Variables in Wrong File
- **Symptom**: Service can't find expected environment variable
- **Cause**: Variable prefix not recognized, went to `custom.env`
- **Fix**: Move variable manually or add prefix to `SERVICE_PREFIXES` in migrate-env.py

### 3. Backup Location
- Legacy `.env` backed up to: `backups/.env.legacy`
- Feature branch dirs backed up to: `backups/environments-enabled.legacy/`

### 4. Re-running Migration
```bash
# Preview what would happen
make migrate-env-dry-run

# Force re-run (removes services-enabled/.env first)
make migrate-env-force

# Manual restore and retry
cp backups/.env.legacy .env
rm services-enabled/.env
make build
```

### 5. Sietch Container Issues
- Container must be built first: `make sietch-build`
- Check container status: `docker compose -f docker-compose.yml ps sietch`
- Container runs with `/app` mapped to project root

## Useful Commands

```bash
# Check current state
ls -la services-enabled/
ls -la backups/

# Preview migration
make migrate-env-dry-run

# Edit environment files
make edit-env-onramp      # Global config
make edit-env-nfs         # NFS settings
make edit-env-external    # External services
make edit-env <service>   # Service-specific

# Force rebuild
make migrate-env-force
make build
```

## Related Documentation

- `docs/migration-from-legacy-env.md` - Full legacy migration details
- `docs/migration-from-feature-branch.md` - Feature branch migration details
- `docs/scaffolding.md` - New scaffolding system

---

## My Specific Issue

[Describe your issue here - what command you ran, what error you saw, what you expected to happen]

## After Resolving Your Issue

Once you've fixed your migration problem, help future users by improving the migration script:

### 1. Identify the Pattern
- What type of variable or configuration caused the issue?
- Is this a one-off edge case or a pattern that could affect others?
- What detection logic was missing?

### 2. Generalize the Fix
Ask your AI assistant to:
- Review `sietch/scripts/migrate-env.py` for where the fix should go
- Determine if the fix belongs in:
  - `GLOBAL_VARS` - Core configuration variables
  - `NFS_PREFIXES` - NFS/SAMBA mount settings
  - `EXTERNAL_PREFIXES` - External service proxy settings
  - `SERVICE_PREFIXES` - Service-specific variable mapping
  - Detection logic (`should_migrate_*` methods)
  - Migration logic (`migrate_*` methods)

### 3. Implement the Improvement
Prompt template for your AI assistant:

> Based on the migration issue I just resolved, please:
> 1. Analyze what caused the problem
> 2. Determine if this could affect other users
> 3. If yes, propose a change to `sietch/scripts/migrate-env.py` that would handle this case automatically
> 4. Include appropriate tests in `sietch/tests/test_migrate_env.py`
> 5. Update `docs/migration-from-legacy-env.md` or `docs/migration-from-feature-branch.md` if the documentation needs clarification

### 4. Submit Your Improvement
- Create a branch: `git checkout -b fix/migration-<description>`
- Make the changes to migrate-env.py
- Run tests: `make test`
- Commit and push
- Open a PR with context about the original issue

### Example Improvements
- Adding a new service prefix to `SERVICE_PREFIXES`
- Adding external service detection to `EXTERNAL_PREFIXES`
- Improving variable categorization logic
- Adding edge case handling for unusual .env formats
