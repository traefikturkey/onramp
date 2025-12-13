# PostgreSQL Consolidation Plan

**Date**: December 13, 2025  
**Status**: In Progress - Phase 1  
**Goal**: Consolidate all PostgreSQL-dependent services to use a single shared postgres container

---

## Executive Summary

OnRamp currently has **11 services** with dedicated PostgreSQL containers. This plan outlines the migration to a single shared `postgres:16` service, reducing container count, simplifying management, and standardizing database operations.

**Approach**: Iterative, test-driven migration
- Start with ONE simple service (healthchecks)
- Test thoroughly, document issues
- Update plan based on learnings
- Commit working changes before proceeding
- Repeat for each service

**Benefits**:
- Reduced resource usage (11 postgres containers → 1)
- Centralized backup and maintenance
- Consistent database version (postgres:16)
- Simplified monitoring and logging
- Standardized credential management

---

## Living Document Process

**This plan will be updated as we learn from each migration.**

After each service migration:
1. ✅ Check off service in `postgres-consolidation-checklist.md`
2. 📝 Document issues/solutions in "Migration Log" section below
3. 🔄 Update migration pattern if needed
4. 💾 Commit working changes with descriptive message
5. ↻ Review and refine approach for next service

---

## Current State Inventory

### Services with Dedicated PostgreSQL (11 total):

**Simple Services** (Good first candidates):
1. ✅ **n8n** - Already migrated (reference implementation)
2. ⏸️ **healthchecks** - Single app, postgres only → **START HERE**
3. ⏸️ **kaneo** - Kanban board, postgres only
4. ⏸️ **mediamanager** - Media library, postgres only

**Medium Complexity** (Multi-container):
5. ⏸️ **nocodb** - No-code platform, postgres:12.17
6. ⏸️ **kaizoku** - Manga downloader, postgres + Redis
7. ⏸️ **tandoor** - Recipe manager, postgres + nginx

**Complex** (Special requirements):
8. ⏸️ **dockerizalo** - Hardcoded credentials, needs refactoring first
9. ⏸️ **paperless-ngx-postgres** - Large multi-service setup
10. ⏸️ **authentik** - Complex auth platform, custom namespace
11. ⏸️ **dawarich** - Requires PostGIS
12. ⏸️ **geopulse** - Requires PostGIS with custom tuning

---

## Migration Pattern (The n8n Model)

### Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│  Service (Default Configuration)                    │
│  ├─ Uses SQLite/lightweight DB by default          │
│  ├─ Works standalone without postgres               │
│  └─ Documented in service YAML                      │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Optional Override (overrides-available/)           │
│  ├─ Connects to shared postgres service            │
│  ├─ Depends on postgres being enabled               │
│  ├─ Uses standard PG_USER/PG_PASS variables        │
│  └─ Database auto-created by sietch                 │
└─────────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────┐
│  Shared Postgres Service                            │
│  ├─ postgres:16 container                           │
│  ├─ Multiple databases (one per service)            │
│  ├─ Shared credentials                              │
│  └─ Single backup point                             │
└─────────────────────────────────────────────────────┘
```

### Metadata Fields

Add to service YAML files:

```yaml
# description: Service description here
# database: postgres              ← Indicates postgres requirement
# database_name: dbname            ← Database to auto-create
# https://service-url.com
```

---

## Phase 1: Foundation & First Service

### Status: 🔄 In Progress

**Goal**: Build automation + Migrate healthchecks

**Tasks:**
- [ ] Create `postgres_manager.py` module
- [ ] Update `scaffold.py` for database auto-creation
- [ ] Test automation with n8n
- [ ] Migrate healthchecks service
- [ ] Document learnings
- [ ] Commit: "feat: add postgres automation and migrate healthchecks"

---

## Migration Log

### Migration 0: n8n (Reference - Already Complete)
**Date**: December 13, 2025  
**Status**: ✅ Complete  
**Issues Found**:
- Network connectivity: Postgres wasn't on traefik network
- Database creation: Manual step required
- Permission issues: /home/node/.n8n directory ownership

**Solutions**:
- Added postgres to traefik network in postgres.yml
- Created postgres_manager.py for automation (planned)
- Fixed with chown before container start

**Commits**:
- `879e3a2`: fix: add traefik network to postgres service
- `2d45a7d`: refactor: generalize n8n-postgres override to use shared postgres

**Lessons Learned**:
- All services need to be on traefik network to resolve DNS
- Database creation should be automated
- Permission handling is critical

---

### Migration 1: healthchecks
**Date**: TBD  
**Status**: ⏸️ Pending  
**Issues Found**:
- TBD

**Solutions**:
- TBD

**Commits**:
- TBD

---

## Next Actions

1. ✅ Create plan document (this file)
2. ✅ Create checklist document
3. ⏳ Create `postgres_manager.py` module
4. ⏸️ Update `scaffold.py` for auto-creation
5. ⏸️ Test automation with n8n
6. ⏸️ Migrate healthchecks

---

**Last Updated**: December 13, 2025 - Initial creation  
**Next Review**: After postgres_manager.py implementation
