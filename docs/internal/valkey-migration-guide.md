# Valkey Migration Guide

This guide explains how Valkey cache consolidation works in OnRamp and how to migrate services to use the shared Valkey infrastructure.

## Overview

Instead of running dedicated Redis/Valkey containers for each service, OnRamp provides a shared Valkey service that supports 16 isolated databases (0-15). Services automatically get assigned unique database numbers when enabled.

## Architecture

- **Shared Service**: `valkey:latest` running on port 6379
- **Database Isolation**: 16 databases (0-15) provide logical separation
- **Auto-Assignment**: Services get unique database numbers via `valkey_manager.py`
- **Scaffold Integration**: Databases are automatically assigned when services are enabled
- **Metadata-Driven**: Service YAMLs declare cache requirements via comments

## Migrated Services

All 12 services now use shared Valkey:

| Service | Database | Connection String |
|---------|----------|-------------------|
| authentik | 0 | `redis://valkey:6379/0` |
| dawarich | 1 | `redis://valkey:6379/1` |
| kaizoku | 2 | `redis://valkey:6379/2` |
| yamtrack | 3 | `redis://valkey:6379/3` |
| newsdash | 4 | `redis://valkey:6379/4` |
| docmost | 5 | `redis://valkey:6379/5` |
| manyfold | 6 | `redis://valkey:6379/6` |
| immich | 7 | `redis://valkey:6379/7` |
| netbox | 8 | `redis://valkey:6379/8` |
| paperless-ngx | 9 | `redis://valkey:6379/9` |
| paperless-ngx-postgres | 10 | `redis://valkey:6379/10` |
| wallabag | 11 | `redis://valkey:6379/11` |

## Service Migration Process

### Manual Migration

1. **Add Metadata** to service YAML:
   ```yaml
   # cache: valkey
   # cache_db: N  # Optional: preferred database number
   ```

2. **Update Connection Strings**:
   - `REDIS_URL`: `redis://valkey:6379/N`
   - `REDIS_HOST`: `valkey`
   - `REDIS_DB`: `N`
   - `REDIS_HOSTNAME`: `valkey`
   - `REDIS_DBINDEX`: `N`

3. **Update Dependencies**:
   ```yaml
   depends_on:
     - valkey
   ```

4. **Remove Dedicated Container**: Delete the old Redis/Valkey service definition

### Automated Migration

Use the `migrate_valkey.py` script:

```bash
cd /apps/onramp
./sietch/scripts/migrate_valkey.py <service-name>

# Dry run to see what would change
./sietch/scripts/migrate_valkey.py <service-name> --dry-run

# Skip backup step
./sietch/scripts/migrate_valkey.py <service-name> --skip-backup
```

The script will:
- Detect dedicated Redis/Valkey containers
- Create RDB backup to `./backups/valkey-migrations/`
- Assign database number via valkey_manager
- Update YAML with connection strings
- Remove dedicated containers
- Create rollback override file
- Verify migration success

## Rollback Process

Each migrated service has a rollback override that restores the dedicated container:

```bash
# Enable rollback
make enable-override <service>-dedicated-redis

# For services that used Valkey originally
make enable-override <service>-dedicated-valkey

# Restart service
make restart <service>
```

Example:
```bash
make enable-override authentik-dedicated-redis
make restart authentik
```

## Valkey Manager

The `valkey_manager.py` tool provides database management:

### List Database Assignments
```bash
./sietch/scripts/valkey_manager.py list-dbs
```

Output:
```
Database Assignments:
  DB 0: authentik
  DB 1: dawarich
  DB 2: kaizoku
  ...
```

### Assign Database to Service
```bash
# Auto-assign next available
./sietch/scripts/valkey_manager.py assign-db <service>

# Request specific database
./sietch/scripts/valkey_manager.py assign-db <service> --preferred-db 5
```

### Get Service's Database
```bash
./sietch/scripts/valkey_manager.py get-db <service>
```

### Release Database
```bash
./sietch/scripts/valkey_manager.py release-db <service>
```

### Flush Database
```bash
# Flush specific database (with confirmation)
./sietch/scripts/valkey_manager.py flush-db 5
```

### Interactive Console
```bash
# Connect to specific database
./sietch/scripts/valkey_manager.py console 0

# Inside console:
127.0.0.1:6379[0]> KEYS *
127.0.0.1:6379[0]> INFO keyspace
```

### Server Info
```bash
# Get Valkey server info
./sietch/scripts/valkey_manager.py info

# Ping server
./sietch/scripts/valkey_manager.py ping
```

## Scaffold Integration

When you enable a service with Valkey metadata, the scaffold system automatically:

1. **Detects Metadata** in service YAML
2. **Checks Valkey Service** is enabled
3. **Assigns Database** via valkey_manager
4. **Logs Assignment**: "Assigned DB N to 'service'"

This happens in Phase -1b of the scaffold build process (before volume creation).

## Connection Patterns

Valkey supports multiple connection string patterns:

### URL Format
```yaml
environment:
  - REDIS_URL=redis://valkey:6379/5
  - CACHE_URL=redis://valkey:6379/5
```

### Host + DB Format
```yaml
environment:
  - REDIS_HOST=valkey
  - REDIS_PORT=6379
  - REDIS_DB=5
```

### Hostname Format
```yaml
environment:
  - REDIS_HOSTNAME=valkey
  - REDIS_DBINDEX=5
```

### Application-Specific
Some services use custom variable names:
```yaml
# Authentik
- AUTHENTIK_REDIS__HOST=valkey
- AUTHENTIK_REDIS__DB=0

# Netbox
- REDIS_HOST=valkey
- REDIS_DB_TASK=8
- REDIS_DB_CACHE=8
```

## Database Assignment Tracking

Assignments are stored in `./etc/.valkey_assignments.json`:

```json
{
  "assignments": {
    "authentik": 0,
    "dawarich": 1,
    "kaizoku": 2
  },
  "last_updated": "2024-01-15T10:30:00"
}
```

## Best Practices

1. **Preferred Database Numbers**: Specify `# cache_db: N` for consistent assignments across environments

2. **Verify Assignments**: After migration, check with `valkey_manager.py list-dbs`

3. **Monitor Memory**: Use `valkey_manager.py info` to check keyspace usage

4. **Backup Before Migration**: The migration script creates RDB backups automatically

5. **Test After Migration**: Verify service functionality after switching to shared Valkey

6. **Keep Rollback Overrides**: Don't delete rollback override files until migration is proven stable

## Troubleshooting

### Service Can't Connect to Valkey

Check if Valkey service is enabled:
```bash
ls -la services-enabled/valkey.yml
```

If not enabled:
```bash
make enable-service valkey
make up valkey
```

### Wrong Database Number

1. Check assignment:
   ```bash
   ./sietch/scripts/valkey_manager.py get-db <service>
   ```

2. Update service YAML metadata:
   ```yaml
   # cache_db: <correct-number>
   ```

3. Reassign:
   ```bash
   ./sietch/scripts/valkey_manager.py release-db <service>
   ./sietch/scripts/valkey_manager.py assign-db <service> --preferred-db <N>
   ```

### Database Collision

If two services try to use the same database:
```bash
# Check all assignments
./sietch/scripts/valkey_manager.py list-dbs

# Release conflicting assignment
./sietch/scripts/valkey_manager.py release-db <service>

# Reassign to different database
./sietch/scripts/valkey_manager.py assign-db <service> --preferred-db <different-N>
```

### Lost Data After Migration

Restore from backup:
```bash
# Find backup
ls -la ./backups/valkey-migrations/

# Use rollback override to restore dedicated container
make enable-override <service>-dedicated-redis
make restart <service>
```

## Advanced Usage

### Flush All Databases

```bash
for db in {0..15}; do
  ./sietch/scripts/valkey_manager.py flush-db $db --force
done
```

### Check Keyspace Per Database

```bash
./sietch/scripts/valkey_manager.py console 0
127.0.0.1:6379[0]> INFO keyspace
```

Output shows memory usage:
```
# Keyspace
db0:keys=42,expires=0,avg_ttl=0
db1:keys=156,expires=5,avg_ttl=3600000
```

### Monitor Active Connections

```bash
./sietch/scripts/valkey_manager.py console
127.0.0.1:6379> CLIENT LIST
```

## See Also

- [PostgreSQL Migration Guide](postgres-migration-guide.md)
- [MariaDB Migration Guide](mariadb-migration-guide.md)
- [Database Consolidation Summary](database-consolidation-summary.md)
