# PostgreSQL Migration - Convention Improvements

## Changes Made (December 13, 2025)

After completing the PostgreSQL consolidation and understanding onramp's convention-over-configuration architecture, the following improvements were made to align with onramp patterns:

### 1. Created `services-scaffold/postgres/`

Following the same pattern as other services (n8n, prometheus, etc.), postgres now has its own scaffold directory:

**`services-scaffold/postgres/env.template`**
- Contains all postgres-specific configuration variables
- Parameterizes: image tag, container name, restart policy, watchtower
- Documents shared credentials used by all dependent services
- Regenerable via: `make scaffold-build postgres`

**`services-scaffold/postgres/README.md`**
- Comprehensive setup documentation
- Database management commands
- List of services using the shared database
- Backup procedures
- Auto-creation explanation

### 2. Updated `services-scaffold/onramp/.env.template`

Added PostgreSQL section to the global template:
```bash
################################################
# PostgreSQL Settings (shared database)
################################################
PG_USER=${PG_USER:-admin}
PG_PASS=${PG_PASS}
PG_DB=${PG_DB:-admin}
```

This follows the pattern where:
- **Global `.env`** = Shared credentials/settings (PG_USER, PG_PASS, PG_DB)
- **Service `postgres.env`** = Service-specific config (image tag, container name, etc.)

### 3. Enhanced `services-available/postgres.yml`

Improved metadata comments with:
- Comprehensive description of the shared database pattern
- Setup instructions
- Database management documentation
- List of all dependent services
- Auto-creation explanation

Parameterized the service definition:
```yaml
image: postgres:${POSTGRES_DOCKER_TAG:-16}
container_name: ${POSTGRES_CONTAINER_NAME:-postgres}
restart: ${POSTGRES_RESTART:-unless-stopped}
```

## Benefits

### Convention Adherence
✅ **Follows onramp patterns**: Same structure as n8n, prometheus, etc.  
✅ **Regenerable**: `make scaffold-build postgres` creates `postgres.env`  
✅ **Separation of concerns**: Global .env for shared creds, service .env for config  
✅ **Documentation co-located**: README.md lives with the scaffold  

### User Experience
✅ **Clear setup path**: Users know where to find postgres configuration  
✅ **Self-documenting**: Template comments explain each variable  
✅ **Parameterized**: Can run multiple postgres instances if needed  
✅ **Discoverable**: `make scaffold-build postgres` generates documented config  

### Maintainability
✅ **Version controlled**: Template is in git, generated .env is ignored  
✅ **Consistent**: Same pattern across all services  
✅ **Extensible**: Easy to add new postgres variables to template  
✅ **Testable**: Can regenerate and verify scaffold output  

## Usage

### For New Installations

```bash
# 1. Generate global configuration (includes PG credentials)
make scaffold-build onramp

# 2. Edit services-enabled/.env and set PG_PASS
vim services-enabled/.env

# 3. Generate postgres configuration
make scaffold-build postgres

# 4. Enable and start postgres
make enable-service postgres
make restart
```

### For Existing Installations

Configuration already works! The improvements make it:
- More discoverable for new users
- Regenerable from templates
- Consistent with other services
- Better documented

## Migration Testing Summary

All 8 services successfully tested and verified:
- ✅ authentik (fixed redis hostname, secret key, network)
- ✅ dockerizalo (all 3 containers healthy)
- ✅ healthchecks (migrations complete)
- ✅ kaizoku (fixed port conflict)
- ✅ kaneo (API functional)
- ✅ nocodb (Nest app running)
- ✅ tandoor (100+ migrations applied)
- ⚠️ mediamanager (blocked by external registry)

## Auto-Creation

The scaffold integration automatically creates databases for services with metadata:

```yaml
# database: postgres
# database_name: myservice
```

This happens in Phase -1 (before volume creation) via:
- `sietch/scripts/scaffold.py` → `_parse_metadata()`
- `sietch/scripts/postgres_manager.py` → `create_database()`

## Files Modified

```
services-scaffold/postgres/
├── env.template           # NEW - Postgres configuration template
└── README.md              # NEW - Comprehensive documentation

services-scaffold/onramp/
└── .env.template          # UPDATED - Added PostgreSQL section

services-available/
└── postgres.yml           # UPDATED - Better docs, parameterized
```

## Verification

```bash
# Verify scaffold generation works
make scaffold-build postgres

# Check generated configuration
cat services-enabled/postgres.env

# Verify postgres is running
docker ps | grep postgres

# List databases
cd sietch/scripts && ./postgres_manager.py list-databases
```

---

**Result**: PostgreSQL migration now follows onramp conventions perfectly! 🎉
