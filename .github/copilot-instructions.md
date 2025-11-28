# OnRamp

Docker Compose-based self-hosted homelab. Traefik reverse proxy + Cloudflare DNS-01 SSL.

**Philosophy:** Disaster Recovery over High Availability. Rebuildable in minutes from backups.

## Architecture

- **Services:** `services-available/*.yml` → symlinked to `services-enabled/`
- **Config:** `services-scaffold/<service>/` templates → `etc/<service>/` and `services-enabled/*.env`
- **Sietch:** Python tool container (`sietch/scripts/`) for scaffolding, backups, DB ops
- **Makefile:** Aggregates compose files dynamically. **Always use `make` commands, never raw `docker compose`.**

## Directory Structure

```
services-available/     # Service definitions (docker-compose YAML)
services-enabled/       # Active symlinks + *.env files
services-scaffold/      # Templates (*.template, *.static, scaffold.yml)
  _templates/           # Service creation templates
etc/                    # Generated configs per service
sietch/scripts/         # Python tools
make.d/                 # Makefile modules
overrides-available/    # Optional service extensions
overrides-enabled/      # Active overrides
```

## Commands

### Services
```bash
make enable-service <name>    # Enable + scaffold
make disable-service <name>   # Disable
make nuke-service <name>      # Disable + remove etc/
make start-service <name>     # Start single
make stop-service <name>      # Stop single
make restart-service <name>   # Restart single
make logs <name>              # View logs
```

### Listing
```bash
make list-services    # Available services
make list-enabled     # Enabled services
make list-games       # Game servers
make list-overrides   # Available overrides
```

### Environment
```bash
make edit-env-onramp   # Global config
make edit-env <name>   # Service config
```

### Scaffold
```bash
make scaffold-build <name>   # Run scaffold
make scaffold-list           # List scaffolds
make scaffold-check <name>   # Check scaffold exists
```

### Backup
```bash
make create-backup           # Local backup
make restore-backup          # Restore latest
make list-backups            # List backups
```

### Database (MariaDB)
```bash
make create-database <name>      # Create DB
make create-user-with-db <name>  # Create user + DB + grant
make show-databases              # List DBs
```

## Sietch Scripts

| Script | Purpose |
|--------|---------|
| scaffold.py | Template rendering, volume creation from compose YAML |
| services.py | Service listing, validation, markdown generation |
| database.py | MariaDB operations via docker exec |
| backup.py | Backup/restore with NFS support |
| cloudflare.py | Cloudflare DNS API |
| migrate-env.py | Legacy .env migration |

## Adding a Service

1. Create `services-available/<name>.yml`
2. (Optional) Create `services-scaffold/<name>/`:
   - `env.template` → `services-enabled/<name>.env`
   - `<file>.template` → `etc/<name>/<file>`
   - `<file>.static` → copied as-is
   - `scaffold.yml` → complex multi-phase operations
3. `make enable-service <name>`

## Conventions

- Use `${VAR:-default}` in YAML for env vars
- Templates use envsubst substitution
- Traefik labels follow existing patterns
- PUID/PGID for container permissions

## Guardrails

- Do not create files without explicit user request
- Always use `make` commands
- Commit all changes when asked (clean `git status`)
