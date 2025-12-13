# Valkey Shared Cache

This scaffold manages configuration for the shared Valkey cache service.

## Overview

Valkey is a Redis-compatible cache server used by multiple OnRamp services. This shared instance replaces individual Redis/Valkey containers that were previously deployed per-service.

## Features

- **16 isolated databases** (0-15) for service separation
- **Auto-assignment** via scaffold integration
- **RDB persistence** for data durability
- **Health checks** for monitoring
- **Convention-based** database allocation

## Setup

1. **Enable the service:**
   ```bash
   make enable-service valkey
   ```

2. **Scaffold will automatically:**
   - Generate `services-enabled/valkey.env` from this template
   - Create data directory: `./media/databases/valkey/data`
   - Initialize assignment tracking: `./etc/.valkey_assignments.json`

3. **Start the service:**
   ```bash
   make restart
   ```

## Service Integration

Services automatically get Valkey database assignments via metadata:

```yaml
# In services-available/yourservice.yml
# cache: valkey
# cache_db: 5  # Optional: preferred database number

services:
  yourservice:
    environment:
      - REDIS_HOST=valkey
      - REDIS_PORT=6379
      - REDIS_DB=5  # Assigned database number
    depends_on:
      - valkey
```

When enabled, scaffold automatically:
1. Detects `# cache: valkey` metadata
2. Assigns next available database (0-15)
3. Records assignment in `./etc/.valkey_assignments.json`

## Database Management

### List Assignments
```bash
cd sietch/scripts
./valkey_manager.py list-dbs
```

Output:
```
Database Assignments:
  DB 0: authentik
  DB 2: kaizoku
  DB 7: immich
  ...
```

### Manual Assignment
```bash
./valkey_manager.py assign-db myservice 3
```

### Get Service Database
```bash
./valkey_manager.py get-db authentik
# Output: 0
```

### Connect to Console
```bash
docker exec -it valkey redis-cli
# or specific database:
docker exec -it valkey redis-cli -n 5
```

## Configuration

Edit `services-enabled/valkey.env` (generated from this template):

```bash
# Docker image
VALKEY_DOCKER_TAG=latest

# Container name
VALKEY_CONTAINER_NAME=valkey

# Restart policy
VALKEY_RESTART=unless-stopped

# Data directory
VALKEY_DIR=./media/databases/valkey/data

# Watchtower auto-updates
VALKEY_WATCHTOWER_ENABLED=true
```

## Services Using Valkey

Currently assigned (check with `./valkey_manager.py list-dbs`):
- authentik (DB 0)
- kaizoku (DB 2)
- dawarich (DB 1)
- yamtrack (DB 3)
- newsdash (DB 4)
- docmost (DB 5)
- manyfold (DB 6)
- immich (DB 7)
- netbox (DB 8)
- paperless-ngx (DB 9)
- paperless-ngx-postgres (DB 10)
- wallabag (DB 11)

## Troubleshooting

### Check if Valkey is running
```bash
docker ps | grep valkey
```

### View logs
```bash
docker logs valkey
```

### Check connections
```bash
docker exec valkey redis-cli INFO clients
```

### Verify database sizes
```bash
for db in {0..15}; do
  echo "DB $db: $(docker exec valkey redis-cli -n $db DBSIZE) keys"
done
```

### Test connection
```bash
docker exec valkey redis-cli PING
# Should return: PONG
```

## Migration from Dedicated Redis

See documentation:
- `documentation/valkey-migration-guide.md` - Complete migration guide
- `documentation/database-consolidation-summary.md` - Overview

Rollback overrides available in `overrides-available/*-dedicated-redis.yml`

## Related Files

- **Service YAML**: `services-available/valkey.yml`
- **Manager Script**: `sietch/scripts/valkey_manager.py`
- **Assignment Tracking**: `./etc/.valkey_assignments.json`
- **Scaffold Integration**: `sietch/scripts/scaffold.py` (phase -1b)
