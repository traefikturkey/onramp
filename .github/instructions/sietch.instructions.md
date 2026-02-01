---
applyTo: "sietch/scripts/**/*.py"
---
# Sietch Python Scripts

Python tools in `sietch/scripts/` for scaffolding, backups, and service operations.

## Available Scripts

| Script | Purpose | Make Target |
|--------|---------|-------------|
| `scaffold.py` | Template rendering, scaffold operations | `make scaffold-build NAME` |
| `services.py` | Service listing, validation, linting, archive | `make list-services` |
| `database.py` | PostgreSQL setup and password generation | `make mariadb-*` |
| `backup.py` | Backup/restore operations | `make create-backup` |
| `migrate-env.py` | Legacy .env migration | `make migrate-env-*` |
| `enable_service.py` | Service enabling with dependency resolution | `make enable-service NAME` |
| `extract_env.py` | Generate env.template from compose YAML | `make create-scaffold-env NAME` |
| `healthcheck_audit.py` | Audit service health checks | `make sietch-run CMD="..."` |
| `migrate_service_env.py` | Service-specific env migrations | `make migrate-service NAME` |
| `traefik_hosts.py` | Sync external hosts to DNS | `make sietch-run CMD="..."` |

## Direct Usage

```bash
make sietch-run CMD="python /scripts/scaffold.py list"
make sietch-run CMD="python /scripts/services.py lint --all"
```

## Key Features

- **Non-TTY Safe**: All scripts detect non-interactive mode and skip prompts
- **Archive Integration**: Services track env files in `services-enabled/archive/` across disable/enable cycles
- **Dependency Resolution**: `enable_service.py` automatically enables required dependencies
- **Password Generation**: Secure random password generation with storage in `.generated_passwords/`
- **Config Versioning**: v1/v2 config versions for tracking service standard compliance

## Architecture

- **IoC Pattern**: `OperationContext` dataclass injected into all operations
- **Base Classes**: `sietch/scripts/operations.py`
- **Type Hints**: Python 3.12+ required
- **Testing**: `make test` runs pytest suite

See [shared context](../shared/sietch-scripts.md) for full architecture and conventions.
