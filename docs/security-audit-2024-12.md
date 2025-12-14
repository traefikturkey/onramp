# Security Audit - December 2024

This document captures security findings from an adversarial review of the sietch scripts and Makefile integration.

## Summary

| Severity | Count | Status |
|----------|-------|--------|
| Critical | 4 | Fixed |
| High | 5 | Documented |
| Medium | 8 | Documented |
| Low | 3 | Documented |

## Critical Issues

### 1. SQL Injection in Database Managers

**Files:** `sietch/scripts/postgres_manager.py`, `sietch/scripts/mariadb_manager.py`

**Issue:** Direct string interpolation of user-controlled input in SQL queries using f-strings.

```python
# VULNERABLE - postgres_manager.py:94
sql = f"SELECT 1 FROM pg_database WHERE datname='{dbname}'"

# VULNERABLE - mariadb_manager.py:113
sql = f"SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME='{dbname}'"
```

**Attack Vector:**
```bash
make postgres-create-db "test'; DROP DATABASE postgres; --"
```

**Impact:** Complete database compromise, data loss, privilege escalation.

**Status:** FIXED - Added input validation with strict regex patterns for database names, usernames.

---

### 2. Password Exposure in Command Line Arguments

**File:** `sietch/scripts/mariadb_manager.py:87`

**Issue:** Password passed as `-p{password}` CLI argument, visible in process listings.

```python
# VULNERABLE
cmd = ["mariadb", "-u", "root", f"-p{password}", dbname, "-e", sql]
```

**Attack Vector:** `ps aux | grep mariadb` shows password.

**Impact:** Credential exposure to any user on the system.

**Status:** FIXED - Use `MYSQL_PWD` environment variable instead.

---

## High Severity Issues

### 3. Docker Socket Mount Without Restrictions

**File:** `Makefile:77`

```makefile
SIETCH_RUN := docker run --rm ... -v /var/run/docker.sock:/var/run/docker.sock ...
```

**Issue:** Full Docker socket access in sietch container. Any vulnerability in sietch scripts = host compromise.

**Impact:** Complete host compromise through container escape.

**Mitigation:** Consider using Docker-out-of-Docker pattern or restricted socket proxy.

---

### 4. Path Traversal in Volume Creation

**File:** `sietch/scripts/scaffold.py:319-350`

**Issue:** Volume paths extracted from service YAML without validation.

```python
volume_path = match.split(":")[0]
abs_path = self.base_dir / volume_path.lstrip("./")
```

**Attack Vector:** Malicious service YAML with `../../etc/passwd` volume mount.

**Mitigation:** Validate paths stay within expected directories.

---

### 5. Unquoted Shell Variables in Makefile

**File:** `Makefile:22`

```makefile
export SERVICE_PASSED_UPCASED := $(shell echo $(SERVICE_PASSED_DNCASED) | tr a-z A-Z)
```

**Issue:** `SERVICE_PASSED_DNCASED` from user input passed to shell unquoted.

**Attack Vector:** `make enable-service 'foo; rm -rf /'`

**Mitigation:** Quote variables: `'$(SERVICE_PASSED_DNCASED)'`

---

### 6. Env File Include Could Execute Code

**File:** `Makefile:9-18`

```makefile
include $(MAKE_INCLUDE_FILES)
```

**Issue:** Malicious `.env` file could contain `$(shell rm -rf /)`.

**Mitigation:** Validate .env files contain only `VAR=value` patterns.

---

### 7. Command Injection in Operations

**File:** `sietch/scripts/operations.py:295-299`

**Issue:** `chown` ownership string from YAML config not validated.

**Mitigation:** Validate user/group against allowed patterns.

---

## Medium Severity Issues

### 8. TOCTOU Race Condition

**File:** `sietch/scripts/postgres_manager.py:98-105`

**Issue:** Time-of-check-to-time-of-use race between `database_exists()` and `CREATE DATABASE`.

**Mitigation:** Use `CREATE DATABASE IF NOT EXISTS` or handle duplicate errors.

---

### 9. Silent Restore Failure

**File:** `sietch/scripts/mariadb_manager.py:205-222`

**Issue:** `restore_database()` just prints instructions, doesn't actually restore.

**Mitigation:** Implement actual restore functionality.

---

### 10. Condition Logic Bug

**File:** `sietch/scripts/operations.py:65-68`

**Issue:** `dir_empty` condition returns True if directory doesn't exist.

```python
if not path.exists() or not path.is_dir():
    return True  # Bug!
```

**Mitigation:** Return False or raise error for non-existent directories.

---

### 11. No Rollback on Scaffold Failure

**File:** `sietch/scripts/scaffold.py:820-827`

**Issue:** If operation 5 of 10 fails, operations 1-4 are left in inconsistent state.

**Mitigation:** Implement rollback mechanism or atomic operations.

---

### 12. Excessive File Permissions

**File:** `sietch/scripts/valkey_manager.py:77`

**Issue:** Assignments file created with 0644 (world-readable).

**Mitigation:** Use 0600 for sensitive files.

---

### 13. No YAML Schema Validation

**File:** `sietch/scripts/scaffold.py:798-808`

**Issue:** Manifest YAML not validated against schema. Typos silently ignored.

**Mitigation:** Add jsonschema or pydantic validation.

---

### 14. Hardcoded Container Names

**Files:** `postgres_manager.py`, `mariadb_manager.py`

**Issue:** Default container names not validated to exist.

**Mitigation:** Verify container exists before operations.

---

### 15. Unquoted Service Names in services.mk

**File:** `make.d/services.mk:39`

**Issue:** Service name passed to shell without quoting.

**Mitigation:** Quote all shell variable expansions.

---

## Low Severity Issues

### 16. Hardcoded Timeout

**File:** `sietch/scripts/adapters/docker_subprocess.py:36`

**Issue:** 30-second timeout may be too short for large operations.

**Mitigation:** Make configurable via environment variable.

---

### 17. Silent chown/chmod Failures

**File:** `sietch/scripts/operations.py:303-308`

**Issue:** Returns success even when chown fails.

**Mitigation:** Log clearly, consider failing the operation.

---

### 18. Unsafe Regex in Volume Parsing

**File:** `sietch/scripts/scaffold.py:310`

**Issue:** `\S*` pattern too greedy, could match across lines.

**Mitigation:** Use more specific pattern: `[^\s:]*`

---

## Recommended Actions

### Immediate (Critical)
1. ~~Add input validation for database names, usernames~~ DONE
2. ~~Use environment variables for passwords instead of CLI args~~ DONE
3. Quote all shell variable expansions in Makefiles

### Short-term (High)
4. Validate paths in scaffold volume creation
5. Add path traversal prevention
6. Consider Docker socket alternatives

### Medium-term
7. Implement YAML schema validation
8. Add rollback mechanism for scaffold
9. Fix condition logic bugs
10. Implement actual restore functionality

---

## Validation Patterns Added

```python
# Database name: alphanumeric, underscore, hyphen, 1-63 chars
DB_NAME_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_-]{0,62}$'

# Username: alphanumeric, underscore, 1-32 chars
USERNAME_PATTERN = r'^[a-zA-Z][a-zA-Z0-9_]{0,31}$'
```

---

## Testing

After fixes, verify with:
```bash
# Should fail with validation error
make postgres-create-db "test'; DROP DATABASE--"

# Should succeed
make postgres-create-db "valid_name"
```
