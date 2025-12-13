# OnRamp

Docker Compose-based self-hosted homelab. Traefik reverse proxy + Cloudflare DNS-01 SSL.

**Philosophy:** Disaster Recovery over High Availability. Rebuildable in minutes from backups.

## Architecture

- **Services:** `services-available/*.yml` → symlinked to `services-enabled/`
- **Config:** `services-scaffold/<service>/` templates → `etc/<service>/` and `services-enabled/*.env`
- **Sietch:** Python tool container (`sietch/scripts/`) for scaffolding, backups, DB ops
- **Makefile:** Aggregates compose files dynamically. **Always use `make` commands.**

## Key Paths

```
services-available/              # Service definitions (docker-compose YAML)
services-enabled/                # Active symlinks + *.env files
services-scaffold/               # Templates (*.template, *.static, scaffold.yml)
services-scaffold/_templates/    # Service creation templates
overrides-available/             # Optional service extensions
overrides-enabled/               # Active overrides
etc/                             # Generated configs per service
sietch/scripts/                  # Python tools (scaffold.py, backup.py, database.py, etc.)
make.d/                          # Makefile includes (services.mk, backup.mk, etc.)
.github/shared/                  # Shared context for sietch scripts, makefiles, scaffolding
```

## Common Commands

### Services
```bash
make enable-service NAME     # Enable + scaffold
make disable-service NAME    # Disable service
make nuke-service NAME       # Remove service and all data
make start-service NAME      # Start single service
make stop-service NAME       # Stop single service
make restart-service NAME    # Restart single service
make logs NAME               # View service logs
```

### Listing
```bash
make list-services           # List available services
make list-enabled            # List enabled services
make list-games              # List game servers
make list-overrides          # List available overrides
```

### Environment
```bash
make edit-env-onramp         # Edit main environment
make edit-env-nfs            # Edit NFS configuration
make edit-env-external       # Edit external services config
make edit-env NAME           # Edit service-specific env
```

### Scaffold
```bash
make scaffold-build NAME     # Re-run scaffold for service
make scaffold-list           # List services with scaffolds
make scaffold-check NAME     # Validate scaffold configuration
```

### Backup
```bash
make create-backup           # Backup configuration
make restore-backup          # Restore from backup
make list-backups            # List available backups
```

### Database (MariaDB)
```bash
make mariadb-console         # Interactive console
make mariadb-list-databases  # List all databases
make mariadb-create-db NAME  # Create database
make mariadb-drop-db NAME    # Drop database
make mariadb-backup-db NAME out.sql  # Backup database
```
Note: Databases are auto-created by scaffolding via `make enable-service`

## Sietch Scripts

| Script | Purpose |
|--------|---------|
| scaffold.py | Template rendering, volume creation |
| services.py | Service listing/validation |
| database.py | MariaDB operations |
| backup.py | Backup/restore |
| cloudflare.py | DNS API operations |
| migrate-env.py | Legacy .env migration |

## Adding Services

1. Create `services-available/<name>.yml`
2. (Optional) Add `services-scaffold/<name>/` with templates
3. `make enable-service <name>`

## Conventions

- Templates: `*.template` (envsubst) or `*.static` (copy as-is)
- Complex scaffolds: `scaffold.yml` manifest with phases
- Env vars: `${VAR:-default}` pattern in YAML

## Guardrails

- Do not create files without explicit user request
- Always use `make` commands, never raw `docker compose`
- Commit all changes when asked (clean `git status`)
