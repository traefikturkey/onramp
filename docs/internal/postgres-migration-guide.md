# PostgreSQL Migration Guide

This guide explains how to migrate services from dedicated PostgreSQL containers to the shared `postgres:16` instance using the automated migration tools.

## Overview

OnRamp now supports a shared PostgreSQL instance that multiple services can use, reducing resource usage and simplifying backups. The migration tools provide safe, automated migration with rollback capabilities.

### Benefits of Shared PostgreSQL

- **Resource Efficiency**: One postgres:16 container instead of many dedicated instances
- **Simplified Backups**: Single backup point for all databases  
- **Easier Management**: One container to monitor and maintain
- **User Isolation**: Optional per-service database users with restricted permissions
- **Auto-Creation**: Databases created automatically via scaffold metadata

## Migration Tools

### 1. postgres_manager.py

Core database operations tool with these commands:

```bash
# Database operations
./postgres_manager.py list-databases                   # List all databases
./postgres_manager.py create-db <name>                 # Create database
./postgres_manager.py drop-db <name>                   # Drop database  
./postgres_manager.py database-exists <name>           # Check existence

# Backup/Restore
./postgres_manager.py backup-db <dbname> <output.dump> # Backup to file
./postgres_manager.py restore-db <dbname> <input.dump> # Restore from file

# User Management
./postgres_manager.py create-user <username> [dbname]  # Create isolated user

# Statistics & Verification
./postgres_manager.py get-stats <dbname>               # Get DB stats (JSON)
./postgres_manager.py verify-db <dbname>               # Verify integrity

# Migration
./postgres_manager.py migrate-from <container> <src_db> <dest_db>

# Console Access
./postgres_manager.py console                          # Interactive psql
```

### 2. migrate_postgres.py

Automated migration orchestration script:

```bash
# Migrate a service
./migrate_postgres.py <service>

# Preview migration (no changes)
./migrate_postgres.py <service> --dry-run

# Verify existing migration
./migrate_postgres.py <service> --verify
```

**What it does:**
1. Detects dedicated postgres container
2. Backs up existing database to `./backups/postgres-migrations/`
3. Migrates data to shared postgres instance
4. Updates service YAML with metadata
5. Creates rollback override file
6. Verifies migration success

**Idempotent**: Safe to run multiple times - skips if already migrated.

### 3. rollback_postgres.py

Rollback to dedicated postgres if needed:

```bash
# Rollback with empty database
./rollback_postgres.py <service>

# Rollback with most recent backup
./rollback_postgres.py <service> --latest-backup

# Rollback with specific backup
./rollback_postgres.py <service> --backup backup.dump

# Preview rollback
./rollback_postgres.py <service> --dry-run
```

**What it does:**
1. Backs up current shared postgres data
2. Enables dedicated postgres override
3. Optionally restores data to dedicated container
4. Cleans up shared postgres database

## Migration Workflow

### Prerequisites

1. **Shared postgres running:**
   ```bash
   make enable-service postgres
   make restart
   ```

2. **Password configured:**
   ```bash
   # Edit services-enabled/.env
   PG_PASS=your_secure_password
   ```

### Step-by-Step Migration

#### 1. Preview Migration (Dry Run)

```bash
cd sietch/scripts
docker run --rm \
  -v /apps/onramp:/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network traefik \
  -u 1000:1000 \
  -w /app/sietch \
  -e UV_CACHE_DIR=/app/.uv-cache \
  sietch sh -c "uv run python scripts/migrate_postgres.py docmost --dry-run"
```

#### 2. Run Migration

```bash
# Same command without --dry-run
docker run --rm \
  -v /apps/onramp:/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network traefik \
  -u 1000:1000 \
  -w /app/sietch \
  -e UV_CACHE_DIR=/app/.uv-cache \
  sietch sh -c "uv run python scripts/migrate_postgres.py docmost"
```

#### 3. Verify Migration

```bash
# Check backup was created
ls -lh backups/postgres-migrations/

# List databases in shared postgres
docker run --rm \
  -v /apps/onramp:/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network traefik \
  -u 1000:1000 \
  -w /app/sietch \
  -e UV_CACHE_DIR=/app/.uv-cache \
  sietch sh -c "uv run python scripts/postgres_manager.py list-databases"

# Get database statistics
docker run --rm \
  -v /apps/onramp:/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network traefik \
  -u 1000:1000 \
  -w /app/sietch \
  -e UV_CACHE_DIR=/app/.uv-cache \
  sietch sh -c "uv run python scripts/postgres_manager.py get-stats docmost"
```

#### 4. Restart Service

```bash
make restart
```

#### 5. Test Application

```bash
# Check logs
docker logs docmost

# Verify service is working
# Test application functionality
```

### Rollback if Needed

If something goes wrong:

```bash
# Rollback to dedicated postgres
docker run --rm \
  -v /apps/onramp:/app \
  -v /var/run/docker.sock:/var/run/docker.sock \
  --network traefik \
  -u 1000:1000 \
  -w /app/sietch \
  -e UV_CACHE_DIR=/app/.uv-cache \
  sietch sh -c "uv run python scripts/rollback_postgres.py docmost --latest-backup"

# Restart service
make restart
```

Or manually:

```bash
make enable-override docmost-dedicated-postgres
make restart
```

## Service Migration Status

### Already Migrated (9 services)

✅ authentik  
✅ dockerizalo  
✅ healthchecks  
✅ kaizoku  
✅ kaneo  
✅ mediamanager  
✅ n8n  
✅ nocodb  
✅ tandoor  

### Simple Migration Candidates (6 services)

These have standard postgres setups and should migrate cleanly:

- **docmost** - Wiki/documentation (postgres:16-alpine)
- **joplin** - Note-taking (postgres:15)
- **spacebin** - Pastebin (postgres:16.3-alpine)
- **manyfold** - 3D model library (postgres:15)
- **netbox** - IPAM/DCIM (postgres:16.4)
- **odoo** - ERP/CRM (postgres:15)

### Complex Migrations (2 services)

Require extra coordination:

- **paperless-ngx** - Multi-service setup (postgres:13)
- **komodo** - Uses FerretDB (postgres:latest)

### Cannot Migrate (3 services)

These require special postgres extensions not available in standard postgres:16:

- **immich** - Requires vector extensions (custom image)
- **geopulse** - Requires PostGIS (postgis/postgis:17-3.5)
- **dawarich** - Requires PostGIS

## Troubleshooting

### Migration Fails

**Check logs:**
```bash
# Migration creates detailed logs
cat backups/postgres-migrations/<service>_<timestamp>.log
```

**Common issues:**
- Source container not running: Start service first
- Permission denied: Check PUID/PGID match between containers
- Disk space: Ensure adequate space in backups directory

### Service Won't Connect After Migration

**Check connection string:**
```yaml
# Should use these patterns:
DATABASE_URL=postgresql://${PG_USER}:${PG_PASS}@postgres:5432/<dbname>

# Or individual variables:
POSTGRES_HOST=postgres
POSTGRES_USER=${PG_USER}
POSTGRES_PASSWORD=${PG_PASS}
POSTGRES_DB=<dbname>
```

**Verify database exists:**
```bash
docker exec postgres psql -U admin -c '\l'
```

**Check container networking:**
```bash
docker exec <service> ping postgres
```

### Data Integrity Concerns

**Compare table counts:**
```bash
# Get stats before migration (save output)
docker exec docmost-db psql -U postgres -d docmost -c '\dt'

# Get stats after migration  
docker exec postgres psql -U admin -d docmost -c '\dt'
```

**Verify row counts:**
```bash
./postgres_manager.py get-stats docmost
```

## Best Practices

### Before Migration

1. **Create full backup:**
   ```bash
   make create-backup-service <service>
   ```

2. **Document current state:**
   ```bash
   docker ps | grep <service>
   docker exec <service>-db psql -U postgres -c '\l'
   ```

3. **Test in staging:** If possible, test migration on non-production instance

### During Migration

1. **Use dry-run first:** Always preview with `--dry-run`
2. **One service at a time:** Don't migrate multiple services simultaneously
3. **Monitor logs:** Watch for errors during migration
4. **Verify data:** Check table counts and row counts after migration

### After Migration

1. **Test thoroughly:** Verify all application features work
2. **Keep backups:** Don't delete migration backups for 30 days
3. **Document changes:** Note any configuration changes needed
4. **Update monitoring:** Update any monitoring configs to point to shared postgres

## Security Considerations

### User Isolation

For better security, create per-service users:

```bash
# Create isolated user for service
./postgres_manager.py create-user docmost_user docmost

# Update service connection to use new user
# Password saved in: ./etc/.db_passwords/docmost_user.txt
```

### Password Management

- Shared credentials in `services-enabled/.env`
- Per-service passwords in `./etc/.db_passwords/`
- Passwords generated with 32-character random strings
- File permissions set to 600 (owner read/write only)

### Network Isolation

All postgres communication happens on the `traefik` network. Services must be on this network to connect.

## Reference

### Service YAML Metadata

After migration, service YAMLs will have:

```yaml
# database: postgres
# database_name: servicename
```

This metadata enables:
- Auto-database creation via scaffold
- Documentation of postgres dependency
- Migration tooling detection

### Connection String Patterns

**Pattern 1: DATABASE_URL**
```yaml
DATABASE_URL=postgresql://${PG_USER}:${PG_PASS}@postgres:5432/<dbname>
```

**Pattern 2: Individual Variables**
```yaml
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=${PG_USER}
POSTGRES_PASSWORD=${PG_PASS}
POSTGRES_DB=<dbname>
```

**Pattern 3: Custom Format (NocoDB)**
```yaml
NC_DB=pg://postgres:5432?u=${PG_USER}&p=${PG_PASS}&d=<dbname>
```

### Backup File Format

- **Format:** PostgreSQL custom format (`pg_dump -Fc`)
- **Location:** `./backups/postgres-migrations/<service>_<timestamp>.dump`
- **Naming:** `<service>_YYYYMMDD_HHMMSS.dump`
- **Compressed:** Yes (built into custom format)
- **Portable:** Can restore to any postgres version >= source

## FAQ

**Q: Can I migrate back to dedicated postgres?**  
A: Yes, use `rollback_postgres.py` or enable the `-dedicated-postgres` override.

**Q: Will migration cause downtime?**  
A: Yes, brief downtime during data migration. Plan accordingly.

**Q: What if migration fails partway?**  
A: Backups are created before any changes. Restore from backup and retry.

**Q: Can I migrate multiple databases from one service?**  
A: Currently one database per service. For multi-DB services, migrate manually.

**Q: Do I need to stop the service before migrating?**  
A: No, but it's recommended to ensure data consistency.

**Q: What about database users besides 'admin'?**  
A: Use `create-user` to create isolated users after migration.

**Q: Can I use a different postgres version?**  
A: Shared postgres is postgres:16. Use overrides for version-specific needs.

**Q: What about postgres extensions?**  
A: Standard postgres:16 extensions work. PostGIS/vector require dedicated containers.

---

**Last Updated:** December 13, 2025  
**Tool Versions:** postgres_manager.py v2.0, migrate_postgres.py v1.0  
**Tested Services:** docmost (dry-run), healthchecks, kaneo, nocodb, tandoor, authentik, kaizoku, dockerizalo
