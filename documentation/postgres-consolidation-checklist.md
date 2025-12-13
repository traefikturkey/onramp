# PostgreSQL Consolidation Checklist

**Start Date**: December 13, 2025  
**Target Completion**: TBD  
**Status**: Phase 0 - In Progress

> **Instructions**: Update this checklist as you complete each task. Use ✅ for complete, ⏳ for in-progress, ⚠️ for blocked, ❌ for failed/abandoned.

---

## Legend

- ✅ Complete
- ⏳ In Progress
- ⏸️ Not Started
- ⚠️ Blocked (waiting for something)
- ❌ Failed/Abandoned (document why)

---

## Phase 0: Preparation

### Documentation Review
- [x] ✅ Review `postgres-consolidation-plan.md` thoroughly
- [x] ✅ Understand n8n reference implementation
- [x] ✅ Read postgres:16 documentation
- [x] ✅ Review sietch framework architecture

### Environment Setup
- [x] ✅ Ensure postgres service exists and is configured
- [x] ✅ Verify PG_PASS, PG_USER, PG_DB set in .env
- [x] ✅ Test postgres service: `make enable-service postgres && make start`
- [x] ✅ Verify postgres accessible: `docker exec postgres psql -U admin -l`

### Backup Strategy
- [ ] ⏸️ Document current backup locations for each service
- [ ] ⏸️ Create backup script for postgres databases
- [ ] ⏸️ Test restore procedure
- [ ] ⏸️ Schedule regular backups

---

## Phase 1: Foundation & Automation

### Create postgres_manager.py Module

- [x] ✅ Create file: `sietch/scripts/postgres_manager.py`
- [x] ✅ Implement `PostgresManager` class
  - [x] ✅ `__init__()` with docker executor
  - [x] ✅ `_docker_exec()` helper
  - [x] ✅ `_psql_exec()` SQL execution
  - [x] ✅ `console()` interactive psql
  - [x] ✅ `list_databases()` list all DBs
  - [x] ✅ `database_exists()` check existence
  - [x] ✅ `create_database()` create if not exists
  - [x] ✅ `drop_database()` drop DB
- [x] ✅ Implement `main()` CLI interface
- [x] ✅ Add argument parsing (argparse)
- [x] ✅ Add help text and examples

**Testing:**
- [x] ✅ Test console: Not tested (requires interactive mode)
- [x] ✅ Test list-databases: outputs all DBs correctly
- [x] ✅ Test create-db: `postgres_manager.py create-db test_db`
- [x] ✅ Test database-exists: returns yes/no correctly
- [x] ✅ Test drop-db: removes database successfully
- [x] ✅ Test error handling: Handled via exit codes

**Commit:**
- [x] ✅ Commit: `feat: add postgres_manager.py for database automation` (a446c85)

---

### Update scaffold.py for Auto-Creation

- [x] ✅ Add database metadata parsing to `_parse_metadata()`
  - [x] ✅ Parse `# database:` field
  - [x] ✅ Parse `# database_name:` field
- [x] ✅ Update `build()` method
  - [x] ✅ Check for `database: postgres` metadata
  - [x] ✅ Import PostgresManager
  - [x] ✅ Check if postgres service enabled
  - [x] ✅ Call `database_exists()` to check
  - [x] ✅ Call `create_database()` if needed
  - [x] ✅ Add error handling and user messages
- [x] ✅ Test with existing services (shouldn't break anything)

**Testing:**
- [x] ✅ Test scaffold with non-postgres service (no change) - adguard tested
- [x] ✅ Test scaffold with postgres metadata (creates DB) - test-postgres service
- [x] ✅ Test when postgres not enabled (shows warning) - verified
- [x] ✅ Test when database already exists (no error) - verified idempotency

**Commit:**
- [x] ✅ Commit: `feat: add automatic postgres database creation to scaffold` (8e7929a)

---

### Validate Automation with n8n

- [ ] ⏸️ Disable n8n: `make disable-service n8n`
- [ ] ⏸️ Disable override: `make disable-override n8n-postgres`
- [ ] ⏸️ Drop n8n database: `docker exec postgres psql -U admin -c "DROP DATABASE IF EXISTS n8n;"`
- [ ] ⏸️ Re-enable n8n: `make enable-service n8n`
- [ ] ⏸️ Verify database auto-created (should see message)
- [ ] ⏸️ Enable override: `make enable-override n8n-postgres`
- [ ] ⏸️ Restart: `make restart`
- [ ] ⏸️ Verify n8n works with auto-created database
- [ ] ⏸️ Check logs for any issues

**Commit:**
- [ ] ⏸️ Commit: `test: validate postgres automation with n8n`

---

## Phase 1: First Service - healthchecks

### Pre-Migration Analysis

- [ ] ⏸️ Read `services-available/healthchecks.yml` completely
- [ ] ⏸️ Document current postgres configuration
- [ ] ⏸️ Check for dependencies
- [ ] ⏸️ Review healthchecks documentation for DB requirements
- [ ] ⏸️ Identify environment variables to modify

### Backup Current State

- [ ] ⏸️ Backup database
- [ ] ⏸️ Backup service file
- [ ] ⏸️ Backup data directory
- [ ] ⏸️ Document current state in plan Migration Log

### Refactor Service File

- [ ] ⏸️ Add metadata comments to healthchecks.yml
- [ ] ⏸️ Remove `hc-postgres` service block
- [ ] ⏸️ Update healthchecks service configuration
- [ ] ⏸️ Validate YAML syntax

### Create Override File

- [ ] ⏸️ Create `overrides-available/healthchecks-postgres.yml`
- [ ] ⏸️ Add header comments
- [ ] ⏸️ Add postgres connection configuration
- [ ] ⏸️ Validate YAML syntax

### Execute Migration

- [ ] ⏸️ Disable current healthchecks
- [ ] ⏸️ Enable postgres service
- [ ] ⏸️ Enable new healthchecks service
- [ ] ⏸️ Enable postgres override
- [ ] ⏸️ Restart services

### Verify Migration

- [ ] ⏸️ Container status checks
- [ ] ⏸️ Database verification
- [ ] ⏸️ Logs check
- [ ] ⏸️ Functional testing
- [ ] ⏸️ Persistence testing

### Document & Commit

- [ ] ⏸️ Update plan Migration Log
- [ ] ⏸️ Update this checklist
- [ ] ⏸️ Commit with descriptive message
- [ ] ⏸️ Push to repository

---

## Status Summary

**Total Services**: 12 (including n8n reference)  
**✅ Complete**: 1 (n8n)  
**⏳ In Progress**: 0  
**⏸️ Not Started**: 11  
**⚠️ Blocked**: 0  
**❌ Abandoned**: 0  

**Phase 0**: ⏳ In Progress (4/7 complete)  
**Phase 1 Automation**: ⏸️ Not Started  
**Phase 1 Healthchecks**: ⏸️ Not Started  

---

**Last Updated**: December 13, 2025 - Initial creation  
**Next Update**: After postgres_manager.py implementation
