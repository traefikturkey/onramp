# MariaDB Migration Guide

This guide explains how MariaDB database consolidation works in OnRamp and how to migrate services to use the shared MariaDB infrastructure.

## Overview

Instead of running dedicated MariaDB/MySQL containers for each service, OnRamp provides a shared MariaDB service with automatic database provisioning. Each service gets its own isolated database on the shared instance.

## Architecture

- **Shared Service**: `mariadb:latest` running on port 3306
- **Database Isolation**: Each service gets a unique database
- **Auto-Provisioning**: Databases are automatically created when services are enabled
- **Scaffold Integration**: Database creation happens during service enablement
- **Metadata-Driven**: Service YAMLs declare database requirements via comments
- **High Performance**: Configured with `max_connections=1000` and UTF-8mb4 support

## Migrated Services

All 8 services now use shared MariaDB:

| Service | Database Name | Original Container |
|---------|--------------|-------------------|
| booklore | booklore | lscr.io/linuxserver/mariadb:11.4.5 |
| firefly3 | firefly | mariadb:latest |
| itflow | itflow | mariadb:10.6.11 |
| paperless-ngx | paperless | mariadb:10 |
| semaphore | semaphore | mysql:8.0 |
| unimus | unimus | mariadb:10 |
| vikunja | vikunja | mariadb:10 |
| wallabag | wallabag | mariadb:latest |

## Service Migration Process

### Manual Migration

1. **Add Metadata** to service YAML:
   ```yaml
   # database: mariadb
   # database_name: mydb
   ```

2. **Update Connection Strings**:
   ```yaml
   environment:
     - DB_HOST=mariadb
     - DB_PORT=3306
     - DB_NAME=mydb
   ```

   Or URL format:
   ```yaml
   environment:
     - DATABASE_URL=jdbc:mariadb://mariadb:3306/mydb
   ```

3. **Update Dependencies**:
   ```yaml
   depends_on:
     - mariadb
   ```

4. **Remove Dedicated Container**: Delete the old database service definition

### Automated Migration

Use the `migrate_mariadb.py` script:

```bash
cd /apps/onramp
./sietch/scripts/migrate_mariadb.py <service-name>

# Dry run to see what would change
./sietch/scripts/migrate_mariadb.py <service-name> --dry-run

# Skip backup step
./sietch/scripts/migrate_mariadb.py <service-name> --skip-backup
```

The script will:
- Detect dedicated MariaDB/MySQL containers
- Create SQL dump backup to `./backups/mariadb-migrations/`
- Create database on shared MariaDB
- Update YAML with connection strings
- Remove dedicated containers
- Create rollback override file
- Verify migration success

## Rollback Process

Each migrated service has a rollback override that restores the dedicated container:

```bash
# Enable rollback
make enable-override <service>-dedicated-mariadb

# For semaphore (originally MySQL)
make enable-override semaphore-dedicated-mysql

# Restart service
make restart <service>
```

Example:
```bash
make enable-override firefly3-dedicated-mariadb
make restart firefly3
```

## MariaDB Manager

The `mariadb_manager.py` tool provides database management:

### List Databases
```bash
./sietch/scripts/mariadb_manager.py list-databases
```

Output:
```
booklore
firefly
itflow
paperless
semaphore
unimus
vikunja
wallabag
```

### Create Database
```bash
./sietch/scripts/mariadb_manager.py create-db <dbname>
```

Creates database with UTF-8mb4 character set and unicode collation:
```sql
CREATE DATABASE IF NOT EXISTS `dbname` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci
```

### Check Database Exists
```bash
./sietch/scripts/mariadb_manager.py database-exists <dbname>
echo $?  # 0 = exists, 1 = doesn't exist
```

### Drop Database
```bash
./sietch/scripts/mariadb_manager.py drop-db <dbname>
```

### Create User
```bash
# Auto-generate password
./sietch/scripts/mariadb_manager.py create-user <username>

# Create user with database ownership
./sietch/scripts/mariadb_manager.py create-user <username> <dbname>
```

Password is saved to `./etc/.db_passwords/<username>.txt` with 600 permissions.

### Backup Database
```bash
./sietch/scripts/mariadb_manager.py backup-db <dbname> <output-file>
```

Creates timestamped SQL dump with:
- Single transaction (consistent backup)
- Stored procedures and triggers
- All data and schema

### Restore Database
```bash
./sietch/scripts/mariadb_manager.py restore-db <dbname> <backup-file>
```

### Get Database Statistics
```bash
./sietch/scripts/mariadb_manager.py get-stats <dbname>
```

Output shows:
```
Database | Tables | Size (MB)
---------|--------|----------
firefly  | 47     | 125.34
```

### Verify Database Integrity
```bash
./sietch/scripts/mariadb_manager.py verify-db <dbname>
```

Runs `CHECK TABLE` on all tables:
```
Checking 47 tables in 'firefly'...
  ✓ accounts: OK
  ✓ budgets: OK
  ✓ transactions: OK
  ...
```

### Migrate from Dedicated Container
```bash
./sietch/scripts/mariadb_manager.py migrate-from <container> <source-db> <dest-db>
```

Example:
```bash
./sietch/scripts/mariadb_manager.py migrate-from firefly_db firefly firefly
```

### Interactive Console
```bash
./sietch/scripts/mariadb_manager.py console
```

Opens mysql client connected to shared MariaDB with root credentials.

## Scaffold Integration

When you enable a service with MariaDB metadata, the scaffold system automatically:

1. **Detects Metadata** in service YAML
2. **Checks MariaDB Service** is enabled
3. **Creates Database** via mariadb_manager
4. **Logs Creation**: "Creating MariaDB database 'dbname'..."

This happens in Phase -1a of the scaffold build process (before volume creation).

## Connection Patterns

MariaDB supports multiple connection string patterns:

### Standard MySQL Environment Variables
```yaml
environment:
  - DB_HOST=mariadb
  - DB_PORT=3306
  - DB_NAME=mydb
  - DB_USER=myuser
  - DB_PASSWORD=secret
```

### JDBC URL Format (Java applications)
```yaml
environment:
  - DATABASE_URL=jdbc:mariadb://mariadb:3306/mydb
```

### Symfony/PHP Format
```yaml
environment:
  - SYMFONY__ENV__DATABASE_DRIVER=pdo_mysql
  - SYMFONY__ENV__DATABASE_HOST=mariadb
  - SYMFONY__ENV__DATABASE_PORT=3306
  - SYMFONY__ENV__DATABASE_NAME=mydb
  - SYMFONY__ENV__DATABASE_USER=myuser
  - SYMFONY__ENV__DATABASE_PASSWORD=secret
```

### MariaDB-Specific Variables
```yaml
environment:
  - MARIADB_HOST=mariadb
  - MARIADB_DATABASE=mydb
  - MARIADB_USER=myuser
  - MARIADB_PASSWORD=secret
```

### Application-Specific
```yaml
# Paperless-ngx
- PAPERLESS_DBENGINE=mariadb
- PAPERLESS_DBHOST=mariadb
- PAPERLESS_DBPORT=3306
- PAPERLESS_DBNAME=paperless

# Vikunja
- VIKUNJA_DATABASE_TYPE=mysql
- VIKUNJA_DATABASE_HOST=mariadb
- VIKUNJA_DATABASE_DATABASE=vikunja
```

## MySQL 8.0 Compatibility

Semaphore was migrated from MySQL 8.0 to MariaDB. MariaDB is generally compatible with MySQL, but be aware:

- **Authentication**: MariaDB uses `mysql_native_password` by default (same as MySQL 5.7)
- **JSON Support**: MariaDB has equivalent JSON functions
- **Window Functions**: Supported in MariaDB 10.2+
- **CTEs**: Supported in MariaDB 10.2+

If you encounter compatibility issues, use the rollback override to restore MySQL 8.0.

## Best Practices

1. **Database Naming**: Use service name as database name for consistency

2. **Credentials**: Use environment variables for passwords, don't hardcode

3. **Backup Before Migration**: Always backup before switching to shared MariaDB

4. **Test After Migration**: Verify all service features work correctly

5. **Monitor Performance**: Check database stats with `get-stats` command

6. **Character Set**: All databases use UTF-8mb4 for full Unicode support

7. **Keep Rollback Overrides**: Don't delete until migration is proven stable

## Shared MariaDB Configuration

The shared MariaDB service (`services-available/mariadb.yml`) is configured for high performance:

```yaml
command:
  - --max_connections=1000          # Support many services
  - --character-set-server=utf8mb4  # Full Unicode
  - --collation-server=utf8mb4_unicode_ci
```

### Required Environment Variables

The shared MariaDB requires `MARIADB_PASS` to be set:

```bash
# In .env file
MARIADB_PASS=your-secure-root-password
```

This password is used for:
- Root user authentication
- Database creation/management
- Migrations

## Troubleshooting

### Service Can't Connect to MariaDB

Check if MariaDB service is enabled and running:
```bash
ls -la services-enabled/mariadb.yml
docker ps | grep mariadb
```

If not enabled:
```bash
make enable-service mariadb
make up mariadb
```

### Database Not Found

1. Check if database exists:
   ```bash
   ./sietch/scripts/mariadb_manager.py database-exists mydb
   ```

2. Create manually if needed:
   ```bash
   ./sietch/scripts/mariadb_manager.py create-db mydb
   ```

3. Verify metadata in service YAML:
   ```yaml
   # database: mariadb
   # database_name: mydb
   ```

### Authentication Failed

1. Verify MARIADB_PASS is set:
   ```bash
   grep MARIADB_PASS .env
   ```

2. Check user credentials in service YAML

3. Recreate user if needed:
   ```bash
   ./sietch/scripts/mariadb_manager.py create-user myuser mydb
   ```

### Connection Refused

1. Check MariaDB is listening:
   ```bash
   docker exec mariadb ss -tlnp | grep 3306
   ```

2. Verify service is on correct network:
   ```yaml
   networks:
     - traefik  # MariaDB is on traefik network
   ```

### Lost Data After Migration

Restore from backup:
```bash
# Find backup
ls -la ./backups/mariadb-migrations/

# Option 1: Restore to shared MariaDB
./sietch/scripts/mariadb_manager.py restore-db mydb ./backups/mariadb-migrations/mydb_TIMESTAMP.sql

# Option 2: Use rollback override
make enable-override myservice-dedicated-mariadb
make restart myservice
```

### Slow Queries

1. Check database size:
   ```bash
   ./sietch/scripts/mariadb_manager.py get-stats mydb
   ```

2. Verify indexes in console:
   ```bash
   ./sietch/scripts/mariadb_manager.py console
   USE mydb;
   SHOW INDEX FROM tablename;
   ```

3. Monitor connections:
   ```sql
   SHOW PROCESSLIST;
   SHOW GLOBAL STATUS LIKE 'Threads_connected';
   ```

## Advanced Usage

### Backup All Databases

```bash
for db in $(./sietch/scripts/mariadb_manager.py list-databases); do
  ./sietch/scripts/mariadb_manager.py backup-db $db "./backups/mariadb-all/\${db}.sql"
done
```

### Verify All Databases

```bash
for db in $(./sietch/scripts/mariadb_manager.py list-databases); do
  echo "Checking $db..."
  ./sietch/scripts/mariadb_manager.py verify-db $db
done
```

### Monitor Database Sizes

```bash
./sietch/scripts/mariadb_manager.py console
SELECT 
  table_schema AS 'Database',
  ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
FROM information_schema.TABLES
GROUP BY table_schema
ORDER BY SUM(data_length + index_length) DESC;
```

### Check MariaDB Version

```bash
docker exec mariadb mysql -u root -p${MARIADB_PASS} -e "SELECT VERSION();"
```

### Optimize All Tables

```bash
./sietch/scripts/mariadb_manager.py console
USE mydb;
OPTIMIZE TABLE tablename;

-- Or all tables
SELECT CONCAT('OPTIMIZE TABLE ', table_name, ';')
FROM information_schema.TABLES
WHERE table_schema = 'mydb';
```

## Password Management

User passwords are stored in `./etc/.db_passwords/`:

```bash
# View saved passwords
ls -la ./etc/.db_passwords/

# Read specific password
cat ./etc/.db_passwords/myuser.txt

# Passwords have restricted permissions
# -rw------- (600) - only owner can read/write
```

## Migration Checklist

Before migrating a service to shared MariaDB:

- [ ] Backup existing database with mysqldump
- [ ] Note current database size
- [ ] Check MySQL/MariaDB version compatibility
- [ ] Verify custom configuration (my.cnf)
- [ ] Document stored procedures/triggers
- [ ] Test restore procedure
- [ ] Plan rollback strategy
- [ ] Schedule maintenance window

After migration:

- [ ] Verify service starts successfully
- [ ] Test critical features
- [ ] Check application logs for errors
- [ ] Verify data integrity
- [ ] Monitor performance
- [ ] Run database integrity check
- [ ] Keep backup for 30 days
- [ ] Document any issues

## See Also

- [Valkey Migration Guide](valkey-migration-guide.md)
- [PostgreSQL Migration Guide](postgres-migration-guide.md)
- [Database Consolidation Summary](database-consolidation-summary.md)
