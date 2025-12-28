---
applyTo: "sietch/scripts/**/*.py"
---
# Sietch Python Scripts

Python tools in `sietch/scripts/` for scaffolding, backups, and service operations.

## Available Scripts

| Script | Purpose | Make Target |
|--------|---------|-------------|
| `scaffold.py` | Template rendering, scaffold operations | `make scaffold-build NAME` |
| `services.py` | Service listing, validation, linting | `make list-services` |
| `database.py` | MariaDB operations | `make mariadb-*` |
| `backup.py` | Backup/restore operations | `make create-backup` |
| `migrate-env.py` | Legacy .env migration | `make migrate-env-*` |
| `healthcheck_audit.py` | Audit service health checks | `make sietch-run CMD="..."` |

## Direct Usage

```bash
make sietch-run CMD="python /scripts/scaffold.py list"
make sietch-run CMD="python /scripts/services.py lint --all"
```

## Architecture

- **IoC Pattern**: `OperationContext` dataclass injected into all operations
- **Base Classes**: `sietch/scripts/operations.py`
- **Type Hints**: Python 3.12+ required
- **Testing**: `make test` runs pytest suite

See [shared context](../shared/sietch-scripts.md) for full architecture and conventions.
