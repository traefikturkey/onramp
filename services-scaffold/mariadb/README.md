# MariaDB Shared Database

This scaffold manages configuration for the shared MariaDB database service.

## Overview

MariaDB is a MySQL-compatible database server used by multiple OnRamp services. This shared instance replaces individual MariaDB/MySQL containers that were previously deployed per-service.

## Features

- **Isolated databases** per service
- **Auto-creation** via scaffold integration
- **Shared credentials** with service-specific overrides
- **High connection limit** (1000 connections)
- **UTF8MB4 support** for modern applications
- **Convention-based** database provisioning

## Setup

1. **Set password in `.env`:**
   ```bash
   # In services-enabled/.env
   MARIADB_PASS=your_secure_password_here
   MARIADB_USER=admin
   ```

2. **Enable the service:**
   ```bash
   make enable-service mariadb
   ```

3. **Scaffold will automatically:**
   - Generate `services-enabled/mariadb.env` from this template
   - Create data directory: `./media/databases/mariadb/data`

4. **Start the service:**
   ```bash
   make restart
   ```

## Service Integration

Services automatically get MariaDB databases via metadata:

```yaml
# In services-available/yourservice.yml
# database: mariadb
# database_name: yourservice

services:
  yourservice:
    environment:
      - DB_HOST=mariadb
      - DB_PORT=3306
      - DB_DATABASE=yourservice
      - DB_USER=${YOURSERVICE_DB_USER:-${MARIADB_USER:-admin}}
      - DB_PASSWORD=${YOURSERVICE_DB_PASS:-${MARIADB_PASS}}
    depends_on:
      - mariadb
```

When enabled, scaffold automatically:
1. Detects `# database: mariadb` metadata
2. Creates database specified in `# database_name: xxx`
3. Uses shared MARIADB_USER/MARIADB_PASS credentials

## Database Management

### List Databases
```bash
cd sietch/scripts
./mariadb_manager.py list-databases
```

### Create Database
```bash
./mariadb_manager.py create-db mynewdb
```

### Drop Database
```bash
./mariadb_manager.py drop-db olddb
```

### Console Access
```bash
./mariadb_manager.py console
# or directly:
docker exec -it mariadb mysql -u admin -p
```

### Backup Database
```bash
./mariadb_manager.py backup-database mydb ./backups/
```

## Configuration

Edit `services-enabled/mariadb.env` (generated from this template):

```bash
# Docker image
MARIADB_DOCKER_TAG=latest

# Container name
MARIADB_CONTAINER_NAME=mariadb

# Restart policy
MARIADB_RESTART=unless-stopped

# Shared credentials
MARIADB_USER=admin
MARIADB_PASS=your_secure_password

# Data directory
MARIADB_DIR=./media/databases/mariadb/data

# Watchtower auto-updates
MARIADB_WATCHTOWER_ENABLED=true
```

## Convention Over Configuration

OnRamp uses a **convention-over-configuration** pattern for database credentials:

### Double Fallback Pattern
```yaml
# Service-specific variable → Shared variable → Default
DB_USER=${FIREFLY_DB_USER:-${MARIADB_USER:-admin}}
DB_PASS=${FIREFLY_DB_PASS:-${MARIADB_PASS}}
```

This means:
1. **Zero-config**: Services work immediately with shared credentials
2. **Override-friendly**: Can set service-specific passwords if needed
3. **Self-documenting**: Variable names show inheritance chain

### Example: firefly3
```yaml
environment:
  - DB_HOST=mariadb
  - DB_DATABASE=firefly
  - DB_USERNAME=${FIREFLY_DB_USERNAME:-${MARIADB_USER:-admin}}
  - DB_PASSWORD=${FIREFLY_DB_PASSWORD:-${MARIADB_PASS}}
```

If you don't set `FIREFLY_DB_USERNAME`, it uses `MARIADB_USER`.  
If you don't set `MARIADB_USER`, it defaults to `admin`.

## Services Using MariaDB

Currently configured:
- booklore (booklore database)
- firefly3 (firefly database)
- itflow (itflow database)
- paperless-ngx (paperless database)
- semaphore (semaphore database)
- unimus (unimus database)
- vikunja (vikunja database)
- wallabag (wallabag database)

## Performance Notes

### Max Connections
Configured for 1000 concurrent connections to support services like vikunja:
```bash
command: --max_connections=1000 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
```

### Character Set
Uses UTF8MB4 (full Unicode support including emojis):
- `--character-set-server=utf8mb4`
- `--collation-server=utf8mb4_unicode_ci`

## Troubleshooting

### Check if MariaDB is running
```bash
docker ps | grep mariadb
```

### View logs
```bash
docker logs mariadb
```

### Check connections
```bash
docker exec mariadb mysql -u admin -p -e "SHOW PROCESSLIST;"
```

### Verify databases
```bash
docker exec mariadb mysql -u admin -p -e "SHOW DATABASES;"
```

### Check max connections
```bash
docker exec mariadb mysql -u admin -p -e "SHOW VARIABLES LIKE 'max_connections';"
```

### Test connection
```bash
docker exec mariadb mysql -u admin -p -e "SELECT 1;"
```

## Migration from Dedicated MariaDB/MySQL

See documentation:
- `documentation/mariadb-migration-guide.md` - Complete migration guide
- `documentation/database-consolidation-summary.md` - Overview

Rollback overrides available in `overrides-available/*-dedicated-mariadb.yml`

## Related Files

- **Service YAML**: `services-available/mariadb.yml`
- **Manager Script**: `sietch/scripts/mariadb_manager.py`
- **Scaffold Integration**: `sietch/scripts/scaffold.py` (phase -1a)
