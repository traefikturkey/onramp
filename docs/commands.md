# Command Reference

Complete list of OnRamp make commands.

## Core Operations

| Command | Description |
|---------|-------------|
| `make` | Start all enabled services |
| `make up` | Start services (foreground, shows logs) |
| `make down` | Stop all services |
| `make restart` | Stop + start all services |
| `make update` | Pull images + restart all services |
| `make logs` | Follow logs for all services |

## Service Lifecycle

| Command | Description |
|---------|-------------|
| `make enable-service NAME` | Enable service + run scaffolding |
| `make disable-service NAME` | Disable service (keeps data in etc/) |
| `make nuke-service NAME` | Remove service AND all data |
| `make start-service NAME` | Start single service |
| `make stop-service NAME` | Stop single service |
| `make restart-service NAME` | Restart single service |
| `make update-service NAME` | Pull image + restart service |
| `make pull-service NAME` | Pull image only |
| `make logs NAME` | View logs for specific service |
| `make attach-service NAME` | Exec bash into running container |

## Environment Management

| Command | Description |
|---------|-------------|
| `make edit-env-onramp` | Edit global .env (HOST_NAME, HOST_DOMAIN, etc.) |
| `make edit-env NAME` | Edit service-specific .env |
| `make edit-env-nfs` | Edit NFS mount configuration |
| `make edit-env-external` | Edit external service URLs |

## Scaffolding

| Command | Description |
|---------|-------------|
| `make scaffold-build NAME` | Re-run scaffold templates for service |
| `make scaffold-list` | List services that have scaffolding |
| `make scaffold-check NAME` | Verify scaffold exists for service |

## Listing

| Command | Description |
|---------|-------------|
| `make list-services` | List all available services |
| `make list-enabled` | List currently enabled services |
| `make list-overrides` | List available overrides |
| `make list-external` | List external service proxies |
| `make list-games` | List game server services |

## External Services

| Command | Description |
|---------|-------------|
| `make enable-external NAME` | Enable external service proxy |
| `make disable-external NAME` | Disable external service proxy |
| `make create-external NAME` | Create new external service from template |

## Overrides

| Command | Description |
|---------|-------------|
| `make enable-override NAME` | Enable service override |
| `make disable-override NAME` | Disable service override |

## Games

| Command | Description |
|---------|-------------|
| `make enable-game NAME` | Enable game server |
| `make disable-game NAME` | Disable game server |

## Backup & Restore

| Command | Description |
|---------|-------------|
| `make create-backup` | Create configuration backup |
| `make restore-backup` | Restore from backup |
| `make list-backups` | List available backups |
| `make create-nfs-backup` | Create backup and copy to NFS server |
| `make create-nfs-backup-direct` | Create backup directly on NFS server |
| `make restore-nfs-backup` | Restore latest backup from NFS server |
| `make list-nfs-backups` | List backups on NFS server |

NFS backups require `NFS_SERVER` and `NFS_BACKUP_PATH` in `services-enabled/.env.nfs`.

## Database (MariaDB)

| Command | Description |
|---------|-------------|
| `make mariadb-console` | Open interactive MariaDB console |
| `make mariadb-list-databases` | List all databases |
| `make mariadb-create-db NAME` | Create new database |
| `make mariadb-drop-db NAME` | Drop database |
| `make mariadb-backup-db NAME FILE` | Backup database to file |

## Utilities

| Command | Description |
|---------|-------------|
| `make check-yaml` | Validate all YAML files |
| `make start-staging` | Start with ACME staging certificates |
| `make down-staging` | Stop staging environment |
| `make clean-acme` | Clear ACME certificate cache |
| `make test` | Run pytest suite |
| `make install` | Initial installation |
| `make help` | Show all available targets |

## Migration

| Command | Description |
|---------|-------------|
| `make migrate-env-dry-run` | Preview .env migration |
| `make migrate-env-force` | Force re-migration of .env |
| `make migrate-service NAME` | Migrate single service .env |

## Sietch (Python Tools)

| Command | Description |
|---------|-------------|
| `make sietch-build` | Build sietch container |
| `make sietch-run CMD="..."` | Run command in sietch container |

Example:
```bash
make sietch-run CMD="python /scripts/scaffold.py list"
make sietch-run CMD="python /scripts/services.py lint --all"
```
