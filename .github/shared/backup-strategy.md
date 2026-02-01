# Backup Strategy

OnRamp's backup system focuses on configuration data. This document explains what's backed up, what's not, and how to create comprehensive backups.

## What's Backed Up

The default backup includes:

| Directory | Contents |
|-----------|----------|
| `etc/` | Service configuration files |
| `services-enabled/` | Enabled service symlinks and env files |
| `overrides-enabled/` | Active override symlinks |

## What's NOT Backed Up

The following are excluded to reduce backup size:

| Pattern | Reason |
|---------|--------|
| `.keep`, `.gitkeep` | Git placeholders |
| `*.log`, `logs/`, `Logs/` | Log files (regeneratable, can be large) |
| `cache/`, `Cache/`, `.cache/`, `__pycache__/` | Cache directories (regeneratable) |
| `etc/plex/Library` | Plex library metadata (huge, regeneratable) |
| `*.iso`, `*.img`, `*.qcow2` | Disk images (large binary artifacts) |
| `*.safetensors`, `*.gguf`, `pytorch_model.bin` | AI model files (downloadable) |
| `etc/games/` | Game server binaries (downloadable) |
| `db/journal/`, `*.db-journal`, `*.db-wal` | Database journals and write-ahead logs |
| `tmp/`, `temp/`, `*.tmp` | Temporary files |

### Database Data

Docker volumes containing database data are NOT backed up by the config backup. Use separate database dumps for complete backups.

## Backup Commands

### Basic Backups

```bash
# Full configuration backup
make create-backup

# Service-specific backup
make create-backup SERVICE=plex

# List available backups
make list-backups
```

### NFS Backups

NFS backups work automatically when configured in `services-enabled/.env.nfs`:

```bash
# Configure NFS (required)
make edit-env-nfs
# Set: NFS_SERVER=your-nas-hostname
# Set: NFS_BACKUP_PATH=/path/to/backup/share
```

Once configured:

```bash
# Create backup and copy to NFS
make create-nfs-backup

# List NFS backups
make list-nfs-backups

# Restore from NFS
make restore-nfs-backup
```

### Service-Specific Backups

```bash
# Backup single service configuration
make create-backup-service SERVICE=plex

# Restore single service from backup
make restore-backup-service SERVICE=plex
```

Service-specific backups include:
- `services-enabled/<service>.env`
- `etc/<service>/` directory
- Relevant override files

### Restore

```bash
# Restore latest backup
make restore-backup

# Restore specific backup
make restore-backup FILE=backups/onramp-config-backup-hostname-24-12-14-1200.tar.gz
```

## Backup Naming Convention

Backups follow the pattern:

```
onramp-config-backup-{hostname}-{YY-MM-DD-HHMM}.tar.gz
```

Example: `onramp-config-backup-homelab-24-12-14-1200.tar.gz`

The hostname helps identify backups from different servers when stored in shared locations.

## Full Backup Procedure

For complete disaster recovery:

### 1. Config Backup (Automatic)

```bash
make create-backup
```

### 2. Database Dumps (Manual)

For each service with a database:

```bash
# PostgreSQL dedicated containers
docker exec myservice-db pg_dump -U myservice myservice > myservice-$(date +%Y%m%d).sql

# MariaDB dedicated containers
docker exec myservice-db mysqldump -u myservice -p myservice > myservice-$(date +%Y%m%d).sql

# Shared PostgreSQL (legacy)
docker exec postgres pg_dump -U username dbname > dbname-$(date +%Y%m%d).sql
```

### 3. Volume Data (Manual)

For services with important volume data:

```bash
# Export named volume
docker run --rm -v myservice-data:/data -v $(pwd):/backup alpine \
  tar czf /backup/myservice-data-$(date +%Y%m%d).tar.gz -C /data .
```

## Restore Procedure

### 1. Deploy Fresh OnRamp

```bash
git clone https://github.com/your/onramp.git
cd onramp
make install
```

### 2. Restore Configuration

```bash
# Copy backup to server
scp backup.tar.gz server:/apps/onramp/backups/

# Restore
make restore-backup FILE=backups/backup.tar.gz
```

### 3. Restore Databases

```bash
# Start database containers
make start-service postgres

# Restore dumps
docker exec -i postgres psql -U admin < dbname.sql
```

### 4. Restart Services

```bash
make restart
```

## Scheduling Backups

### Cron Job Example

```bash
# Daily config backup at 2 AM
0 2 * * * cd /apps/onramp && make create-nfs-backup

# Weekly database dumps at 3 AM on Sundays
0 3 * * 0 cd /apps/onramp && ./scripts/backup-databases.sh
```

### Database Backup Script

Create `/apps/onramp/scripts/backup-databases.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/apps/onramp/backups/databases"
DATE=$(date +%Y%m%d)
mkdir -p "$BACKUP_DIR"

# Backup all PostgreSQL containers
for container in $(docker ps --filter "name=-db" --format "{{.Names}}" | grep -E "postgres|pg"); do
  docker exec "$container" pg_dumpall -U postgres > "$BACKUP_DIR/${container}-${DATE}.sql"
done

# Backup all MariaDB containers
for container in $(docker ps --filter "name=-db" --format "{{.Names}}" | grep -E "mariadb|mysql"); do
  docker exec "$container" mysqldump --all-databases -u root -p"$MYSQL_ROOT_PASSWORD" > "$BACKUP_DIR/${container}-${DATE}.sql"
done

# Cleanup old backups (keep 7 days)
find "$BACKUP_DIR" -name "*.sql" -mtime +7 -delete
```

## Custom Exclusions

Add exclusions via environment variable:

```bash
# In services-enabled/.env
ONRAMP_BACKUP_EXCLUSIONS="etc/large-service etc/another-service/data"
```

Or pass directly:

```bash
docker run --rm -v $(pwd):/app sietch python /scripts/backup.py create \
  --exclude "etc/myservice/cache" \
  --exclude "etc/myservice/logs"
```

## Backup Size Optimization

If backups are too large:

1. **Audit directories**: `du -sh etc/*/ | sort -h`
2. **Find large files**: `find etc -type f -size +50M`
3. **Add exclusions**: Update `DEFAULT_EXCLUSIONS` in `backup.py` or use environment variable

Current exclusions target common space-wasters but your setup may have unique needs.

## Recovery Testing

Periodically test your backup/restore process:

1. Create backup on production
2. Copy to test environment
3. Restore and verify services start
4. Check application functionality
5. Verify data integrity

Document any issues and adjust procedures accordingly.
