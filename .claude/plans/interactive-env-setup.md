# Plan: Interactive Environment Setup Wizard

## Overview

Replace the current "open editor" flow during `make install` with an interactive prompting wizard that guides users through required environment variables with helpful context.

## Scope

### Main `.env` Variables (Always Prompted)

| Variable | Type | Help Text |
|----------|------|-----------|
| `HOST_NAME` | text | Server hostname (used in URLs) |
| `HOST_DOMAIN` | text | Your domain name (e.g., example.com) |
| `TZ` | choice/text | Timezone (picker if system is UTC) |
| `CF_API_EMAIL` | text | Cloudflare account email |
| `CF_DNS_API_TOKEN` | sensitive | Cloudflare API token |

### Auto-Detected (No Prompt)

- `PUID` - from current user's UID
- `PGID` - from current user's GID

### Conditional NFS Flow

```
Do you plan to use NFS for media files? [y/N]
  → If yes: prompt for NFS_SERVER only
```

### Deferred (Not in Scope)

- `.env.external` interactive setup (revisit later)

## Behavior

1. Skip variables that already have non-empty values
2. Sensitive fields hide input (like password prompts)
3. Offer "skip wizard, edit manually" escape hatch
4. Timezone picker shows common zones only when system TZ is UTC

## Implementation Tasks

### Task 1: Create Core Prompting Module

**File:** `sietch/scripts/env_wizard.py`

**Subtasks:**
- [ ] 1.1: Define `EnvVariable` dataclass with fields: `name`, `help_text`, `sensitive`, `required`, `default`, `choices`
- [ ] 1.2: Define `MAIN_ENV_VARS` list with metadata for HOST_NAME, HOST_DOMAIN, TZ, CF_API_EMAIL, CF_DNS_API_TOKEN
- [ ] 1.3: Define `NFS_ENV_VARS` list with metadata for NFS_SERVER
- [ ] 1.4: Implement `prompt_text()` - basic text input with help display
- [ ] 1.5: Implement `prompt_sensitive()` - hidden input using `getpass`
- [ ] 1.6: Implement `prompt_choice()` - numbered menu selection

**Agent:** `python-pro` (opus) - Core business logic, needs careful design

### Task 2: Implement Timezone Picker

**Subtasks:**
- [ ] 2.1: Detect current system timezone
- [ ] 2.2: Define `COMMON_TIMEZONES` list (US + Western Europe)
- [ ] 2.3: Implement `prompt_timezone()` - shows picker only if system is UTC, otherwise uses system TZ
- [ ] 2.4: Include "Other (enter manually)" option

**Agent:** `python-pro` (haiku) - Straightforward logic

### Task 3: Implement Env File I/O

**Subtasks:**
- [ ] 3.1: Implement `load_env_file()` - parse existing env file, preserve comments
- [ ] 3.2: Implement `get_existing_value()` - check if variable already set (non-empty)
- [ ] 3.3: Implement `update_env_file()` - write/update variables while preserving structure
- [ ] 3.4: Handle file creation if env file doesn't exist yet

**Agent:** `python-pro` (haiku) - File I/O, can reuse patterns from existing migrate_env.py

### Task 4: Implement Main Wizard Flow

**Subtasks:**
- [ ] 4.1: Implement `run_wizard()` main entry point
- [ ] 4.2: Detect PUID/PGID from environment or `os.getuid()`/`os.getgid()`
- [ ] 4.3: Prompt for main env vars (skip if already set)
- [ ] 4.4: Ask NFS conditional question
- [ ] 4.5: If NFS yes, prompt for NFS_SERVER
- [ ] 4.6: Implement "skip wizard" escape hatch at start
- [ ] 4.7: Write all collected values to appropriate env files

**Agent:** `python-pro` (sonnet) - Orchestration logic, moderate complexity

### Task 5: Integrate with Makefile

**File:** `make.d/install.mk` and `make.d/sietch.mk`

**Subtasks:**
- [ ] 5.1: Create `env-wizard` Make target that runs the Python script
- [ ] 5.2: Hook wizard into `ensure-env` flow (after basic template copy)
- [ ] 5.3: Only run wizard in interactive mode (`[ -t 0 ]` check)
- [ ] 5.4: Ensure wizard runs after Docker is available (post-bootstrap)

**Agent:** `Bash` (haiku) - Makefile edits, straightforward

### Task 6: Write Tests

**File:** `sietch/tests/test_env_wizard.py`

**Subtasks:**
- [ ] 6.1: Test `EnvVariable` dataclass
- [ ] 6.2: Test `load_env_file()` and `update_env_file()`
- [ ] 6.3: Test `get_existing_value()` skips set variables
- [ ] 6.4: Test timezone detection logic
- [ ] 6.5: Mock stdin for prompting tests
- [ ] 6.6: Test NFS conditional flow

**Agent:** `python-pro` (sonnet) - Test design needs thought

### Task 7: Update Documentation

**Subtasks:**
- [ ] 7.1: Update README install section to mention interactive setup
- [ ] 7.2: Update `.claude/CLAUDE.md` if needed

**Agent:** `Bash` (haiku) - Simple doc updates

## File Structure

```
sietch/
  scripts/
    env_wizard.py          # New - main wizard module
  tests/
    test_env_wizard.py     # New - tests

make.d/
  sietch.mk                # Modified - add env-wizard target
  install.mk               # Modified - hook wizard into flow
```

## Help Text Content

### HOST_NAME
```
Server hostname (will be used in service URLs)
Example: myserver
```

### HOST_DOMAIN
```
Your domain name for SSL certificates and service URLs
Example: example.com
```

### CF_API_EMAIL
```
Email address for your Cloudflare account
```

### CF_DNS_API_TOKEN
```
Cloudflare API token for DNS-01 SSL certificate challenges

Create one at: https://dash.cloudflare.com/profile/api-tokens
  1. Click "Create Token"
  2. Use "Edit zone DNS" template
  3. Zone Resources: Include → Specific zone → your domain
  4. Copy the generated token
```

### NFS_SERVER
```
IP address or hostname of your NFS server
Example: 192.168.1.100 or nas.local
```

## Timezone Choices

```python
COMMON_TIMEZONES = [
    ("US/Eastern", "US Eastern"),
    ("US/Central", "US Central"),
    ("US/Mountain", "US Mountain"),
    ("US/Pacific", "US Pacific"),
    ("America/New_York", "America/New_York"),
    ("America/Chicago", "America/Chicago"),
    ("America/Denver", "America/Denver"),
    ("America/Los_Angeles", "America/Los_Angeles"),
    ("Europe/London", "Europe/London (GMT/BST)"),
    ("Europe/Paris", "Europe/Paris (CET/CEST)"),
    ("Europe/Berlin", "Europe/Berlin (CET/CEST)"),
    ("Europe/Amsterdam", "Europe/Amsterdam (CET/CEST)"),
]
```

## Execution Order

1. `make install` called
2. Bootstrap runs if Docker not available
3. Docker now available, `make build` runs
4. `ensure-env` target runs
5. Basic env files created from templates (existing behavior)
6. **New:** `env-wizard` target runs if interactive terminal
7. Wizard prompts for missing required values
8. Values written to env files
9. Build continues

## Rollback / Edge Cases

- If user Ctrl+C during wizard: partial values may be written, but re-running will skip already-set values
- If running non-interactively: wizard skipped, falls back to template defaults
- If all values already set: wizard prints "All required values configured" and exits

## Estimated Effort

| Task | Complexity |
|------|------------|
| Task 1: Core Module | Medium |
| Task 2: Timezone | Low |
| Task 3: File I/O | Low |
| Task 4: Main Flow | Medium |
| Task 5: Makefile | Low |
| Task 6: Tests | Medium |
| Task 7: Docs | Low |

## Dependencies

- Python 3.x (available in Sietch container)
- `getpass` module (stdlib)
- No external dependencies needed
