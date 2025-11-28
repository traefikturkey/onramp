# OnRamp

Docker Compose-based self-hosted homelab. Traefik reverse proxy + Cloudflare DNS-01 SSL.

## Architecture

- **Services:** `services-available/*.yml` → symlinked to `services-enabled/`
- **Config:** `services-scaffold/<service>/` templates → `etc/<service>/` and `services-enabled/*.env`
- **Sietch:** Python tool container (`sietch/scripts/`) for scaffolding, backups, DB ops
- **Makefile:** Aggregates compose files dynamically. **Always use `make` commands.**

## Key Paths

```
services-available/     # Service definitions (docker-compose YAML)
services-enabled/       # Active symlinks + *.env files
services-scaffold/      # Templates (*.template, *.static, scaffold.yml)
etc/                    # Generated configs per service
sietch/scripts/         # Python tools (scaffold.py, backup.py, database.py, etc.)
make.d/                 # Makefile includes (services.mk, backup.mk, etc.)
```

## Common Commands

```bash
make enable-service <name>   # Enable + scaffold
make disable-service <name>  # Disable
make start-service <name>    # Start single service
make logs <name>             # View logs
make list-services           # List available
make list-enabled            # List enabled
make create-backup           # Backup config
make scaffold-build <name>   # Re-run scaffold
```

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
