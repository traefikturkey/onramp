# Cache & Database Consolidation Testing Report

**Branch:** `cache-db-consolidation`  
**Date:** 2025-12-13  
**Status:** ⚠️ Partial Testing Complete

## Summary

Successfully migrated 20 services to shared infrastructure (12 to Valkey, 8 to MariaDB), but only 2 services have been tested so far.

## Infrastructure Status

### ✅ Valkey (Shared Redis Cache)
- **Image:** `valkey/valkey:latest` ✅ (fixed from `valkey:latest`)
- **Status:** Running and healthy
- **Connections:** 14 clients connected
- **Port:** 6379
- **Databases:** 16 available (0-15)

### ✅ MariaDB (Shared Database)
- **Image:** `mariadb:latest`
- **Status:** Running
- **Port:** 3306
- **Max Connections:** 1000
- **Character Set:** utf8mb4

### ✅ PostgreSQL (Existing Shared Database)
- **Status:** Running (already in production)

## Environment Configuration Issues Found

### Critical Issues Fixed

1. **Missing `.env` Symlink**
   - **Problem:** Docker Compose v1 looks for `.env` in project root, not `services-enabled/`
   - **Solution:** Created symlink: `.env` → `services-enabled/.env`
   - **Command:** `ln -sf services-enabled/.env .env`
   - **Status:** ✅ Fixed

2. **Wrong Valkey Image Name**
   - **Problem:** Used `valkey:latest` which doesn't exist on Docker Hub
   - **Correct Image:** `valkey/valkey:latest`
   - **Status:** ✅ Fixed and committed (0997e1f)

3. **Missing MARIADB_PASS Environment Variable**
   - **Problem:** `services-available/mariadb.yml` requires `MARIADB_PASS` but it wasn't in `.env`
   - **Solution:** Added to `services-enabled/.env`
   - **Status:** ✅ Fixed (not committed - .env is gitignored)

## Services Tested (2/20)

### ✅ authentik (Valkey DB 0)
- **Migration:** ✅ Successful
- **Old Container:** `authentik_redis` (removed)
- **New Connection:** Shared valkey on DB 0
- **Status:** Running and healthy
- **Data Verification:** 24 keys in valkey DB 0 with `authentik_cache:*` prefix
- **Container Logs:** No errors, normal operation
- **Issues:** None

### ⚠️ kaizoku (Valkey DB 2... or is it?)
- **Migration:** ⚠️ Partial success
- **Old Container:** `kaizoku-redis` (removed)
- **New Connection:** Shared valkey
- **Assigned DB:** 2 (in metadata and environment variables)
- **Actual DB Used:** 0
- **Status:** Running, functionally working
- **Data Verification:** Keys with `bull:*` prefix found in DB 0, none in DB 2
- **Environment Check:** `REDIS_DB=2` is set correctly in container
- **Issue:** Kaizoku appears to ignore `REDIS_DB` environment variable and defaults to DB 0
- **Impact:** Minor - service works but shares DB with authentik instead of using isolated DB
- **Recommendation:** Investigate kaizoku's redis client configuration

## Services NOT Tested (18/20)

### Important: Immich Cannot Be Migrated
**immich** is listed in the Valkey migrations but **still uses its own dedicated postgres database**. This is intentional because:
- Immich requires `postgres:14-vectorchord0.4.3-pgvectors0.2.0` (custom image with vector extensions)
- Our shared postgres:latest doesn't have these extensions
- Immich's postgres container cannot be removed without breaking vector search functionality
- Only the Redis/Valkey migration was performed for immich

**Recommendation:** Remove immich from documentation as a "migrated" service or document it as "partial migration (cache only)"

### Valkey Migrations (10 untested)
1. dawarich - DB 1
2. yamtrack - DB 3
3. newsdash - DB 4
4. docmost - DB 5
5. manyfold - DB 6
6. immich - DB 7
7. netbox - DB 8
8. paperless-ngx - DB 9
9. paperless-ngx-postgres - DB 10
10. wallabag - DB 11

### MariaDB Migrations (8 untested)
1. booklore - `booklore` database
2. firefly3 - `firefly` database
3. itflow - `itflow` database
4. paperless-ngx - `paperless` database
5. semaphore - `semaphore` database
6. unimus - `unimus` database
7. vikunja - `vikunja` database
8. wallabag - `wallabag` database

## Testing Procedure Executed

1. ✅ Enabled valkey service: `make enable-service valkey`
2. ✅ Enabled mariadb service: `make enable-service mariadb`
3. ✅ Fixed `.env` symlink issue
4. ✅ Fixed valkey image name
5. ✅ Added MARIADB_PASS to .env
6. ✅ Started services: `make start`
7. ✅ Verified infrastructure running: `docker ps`
8. ✅ Checked authentik logs: `docker logs authentik_server`
9. ✅ Checked kaizoku logs: `docker logs kaizoku`
10. ✅ Verified valkey connections: `docker exec valkey redis-cli INFO clients`
11. ✅ Checked database usage: `for db in {0..11}; do docker exec valkey redis-cli -n $db DBSIZE; done`
12. ✅ Verified keys in DB 0: `docker exec valkey redis-cli -n 0 KEYS "*"`

## Known Issues

### 1. Kaizoku Redis Database Selection
- **Severity:** Low
- **Description:** Kaizoku ignores `REDIS_DB=2` environment variable and uses DB 0
- **Workaround:** Accept DB sharing with authentik (minimal impact)
- **Investigation Needed:** Check kaizoku source code or documentation for proper redis DB configuration
- **Possible Causes:**
  - Kaizoku may not support `REDIS_DB` variable
  - May require different variable name
  - May require connection string format instead
  - BullMQ (job queue library) may have its own DB configuration

### 2. .env Symlink Not in Git
- **Severity:** Low (documentation issue)
- **Description:** The `.env` → `services-enabled/.env` symlink is required but not documented
- **Solution:** Document in setup instructions and create script to set it up
- **Impact:** Fresh clones will fail until symlink is created

## Recommendations

### Immediate (Before Merge)
1. ✅ Fix valkey image name (DONE - 0997e1f)
2. ✅ Create .env.example with all required variables (DONE)
3. ⏳ Test at least 2-3 more Valkey services
4. ⏳ Test at least 2-3 MariaDB services
5. ⏳ Document .env symlink requirement in migration guides
6. ⏳ Investigate kaizoku DB selection issue

### Short Term (Post Merge)
1. Test all remaining services (18 services)
2. Create automated testing script
3. Add health checks for database connectivity
4. Performance testing under load
5. Document any additional service-specific issues

### Long Term
1. Create monitoring dashboard for shared infrastructure
2. Set up alerts for connection limits
3. Document backup/restore procedures for shared databases
4. Create migration rollback testing procedures

## Required Setup for Fresh Systems

```bash
# 1. Create .env symlink (required for Docker Compose v1)
cd /apps/onramp
ln -sf services-enabled/.env .env

# 2. Ensure services-enabled/.env has required variables
# - PG_PASS=<secure-password>
# - PG_USER=admin
# - MARIADB_PASS=<secure-password>
# - MARIADB_USER=admin

# 3. Enable infrastructure services
make enable-service postgres
make enable-service valkey
make enable-service mariadb

# 4. Start services
make start
```

## Database Connection Verification Commands

### Valkey
```bash
# Check connections
docker exec valkey redis-cli INFO clients

# Check database sizes
for db in {0..15}; do 
  echo "=== DB $db ===" 
  docker exec valkey redis-cli -n $db DBSIZE
done

# View keys in specific database
docker exec valkey redis-cli -n 0 KEYS "*"
```

### MariaDB
```bash
# List databases
docker exec mariadb mysql -u admin -p${MARIADB_PASS} -e "SHOW DATABASES;"

# Check connections
docker exec mariadb mysql -u admin -p${MARIADB_PASS} -e "SHOW PROCESSLIST;"

# Connect to specific database
docker exec -it mariadb mysql -u admin -p${MARIADB_PASS} <database-name>
```

### PostgreSQL
```bash
# List databases
docker exec postgres psql -U admin -c "\l"

# Check connections
docker exec postgres psql -U admin -c "SELECT datname, usename, application_name FROM pg_stat_activity;"
```

## Next Steps

1. **Enable and test additional services** (priority: high)
   - Pick 2-3 Valkey services that are low-risk
   - Pick 2-3 MariaDB services that are low-risk
   - Monitor logs carefully
   - Verify data is being stored correctly

2. **Investigate kaizoku DB issue** (priority: medium)
   - Check kaizoku documentation
   - Test if it supports multiple Redis DBs
   - May need to update migration documentation

3. **Update documentation** (priority: high)
   - Add .env symlink requirement to all migration guides
   - Document testing results
   - Add troubleshooting section

4. **Create automated testing** (priority: medium)
   - Script to enable each service
   - Health check verification
   - Database connectivity testing
   - Rollback testing

## Testing Checklist Template

For each service:
- [ ] Enable service: `make enable-service <service-name>`
- [ ] Start service: `make start`
- [ ] Check container status: `docker ps | grep <service-name>`
- [ ] Check container logs: `docker logs <service-name> | tail -50`
- [ ] Verify database/cache connection
- [ ] Test basic functionality
- [ ] Check for errors in infrastructure logs
- [ ] Document any issues found
- [ ] Test rollback if issues found

## Conclusion

Initial testing shows the infrastructure **works correctly** but has limited validation. The valkey and mariadb services are running successfully, and the two tested services (authentik, kaizoku) are functional. However:

- ⚠️ **Only 2 of 20 migrated services tested** (10% coverage)
- ⚠️ **Kaizoku DB assignment issue needs investigation**
- ✅ **Core infrastructure is solid**
- ✅ **Migration code is well-structured**
- 📋 **Extensive testing still required before production merge**

**Recommendation:** Continue testing with 4-6 more services before considering merge to main branch.
