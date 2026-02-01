# Service Dependency Resolution Implementation Plan

## Overview

Add automatic dependency resolution and optional service wizard prompts to `make enable-service`.

## Requirements Summary

1. **Auto-resolve `depends_on`**: Parse YAML, recursively enable required dependencies with informational messages
2. **Optional services with wizard**: Comment metadata declares optional related services with prompts
3. **Support both grouped and individual optional services**
4. **Recursive**: Follow transitive dependencies and prompt for optional deps at each level
5. **Enable as we go**: Process each service's questions and enable before moving to next

## Comment Metadata Format

### Individual Optional Service
```yaml
# optional-service: ollama
# optional-prompt: Enable Ollama for AI document processing?
```

### Grouped Optional Services
```yaml
# optional-group: ai-features
# optional-group-prompt: Enable AI features (Ollama + OpenWebUI)?
# optional-group-services: ollama, openwebui
```

Multiple groups/individuals can be defined in a single YAML file.

## Implementation Steps

### Step 1: Extend ServiceManager metadata parsing

**File**: `sietch/scripts/services.py`

Extend `_parse_metadata()` to capture:
- `optional-service` / `optional-prompt` pairs
- `optional-group` / `optional-group-prompt` / `optional-group-services` sets

Return structure:
```python
{
    # existing fields...
    "optional_services": [
        {"service": "ollama", "prompt": "Enable Ollama for AI?"},
    ],
    "optional_groups": [
        {"name": "ai-features", "prompt": "Enable AI features?", "services": ["ollama", "openwebui"]},
    ],
}
```

### Step 2: Add YAML dependency parser

**File**: `sietch/scripts/services.py` (or new `dependencies.py`)

Add method to parse actual `depends_on` from service YAML:
```python
def get_depends_on(self, service: str) -> list[str]:
    """Parse depends_on from service YAML, returning external service names."""
```

Logic:
1. Load YAML with `yaml.safe_load()`
2. Find all `depends_on` lists across all service definitions
3. Filter to only services NOT defined in the same YAML file (external deps)
4. Return list of external service names

### Step 3: Create dependency resolution wizard

**File**: `sietch/scripts/enable_service.py` (new file)

Main entry point for enhanced enable-service flow:

```python
class EnableServiceWizard:
    def __init__(self, base_dir: str = "/app"):
        self.manager = ServiceManager(base_dir)
        self.scaffolder = Scaffolder(base_dir)
        self.enabled_this_session: set[str] = set()  # track to avoid loops

    def enable_service(self, service: str) -> bool:
        """Enable a service with dependency resolution and optional prompts."""

    def _resolve_required_deps(self, service: str) -> list[str]:
        """Get list of required deps that need enabling (recursive)."""

    def _prompt_optional_services(self, service: str) -> list[str]:
        """Prompt for optional services, return list to enable."""

    def _do_enable(self, service: str) -> bool:
        """Actually enable a single service (symlink + scaffold)."""
```

Flow for `enable_service(paperless-ngx)`:
1. Check if already enabled → skip
2. Parse `depends_on` from YAML
3. For each external dependency not yet enabled:
   - Print "Enabling required dependency: {dep}"
   - Recursively call `enable_service(dep)` (this handles dep's deps and optionals)
4. Parse optional metadata
5. For each optional group/service:
   - Prompt user with yes/no
   - If yes, recursively call `enable_service()` for each
6. Actually enable this service (symlink + scaffold)

### Step 4: Update Makefile integration

**File**: `make.d/services.mk`

Replace current `enable-service` target to call new Python script:

```makefile
enable-service:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
	@$(SIETCH_RUN) python /scripts/enable_service.py enable '$(SERVICE_PASSED_DNCASED)'
else
	@echo "No such service file ./services-available/$(SERVICE_PASSED_DNCASED).yml!"
endif
```

The Python script handles:
- Symlink creation
- Archive restoration check
- Dependency resolution
- Optional service prompts
- Scaffold execution
- Permission fixes

### Step 5: Add tests

**File**: `sietch/tests/test_enable_service.py`

Test cases:
- Service with no dependencies enables normally
- Service with `depends_on` auto-enables dependencies
- Informational message printed for auto-enabled deps
- Optional service prompt shows correctly
- Grouped optional services prompt works
- Recursive dependency resolution works
- Circular dependency detection
- Already-enabled services are skipped

### Step 6: Update documentation

**Files**:
- `.claude/CLAUDE.md` - Add optional service metadata format
- `.github/shared/scaffold-templates.md` - Document new metadata fields
- `docs/` - User-facing documentation for optional services

## File Changes Summary

| File | Change Type |
|------|-------------|
| `sietch/scripts/services.py` | Modify - extend `_parse_metadata()`, add `get_depends_on()` |
| `sietch/scripts/enable_service.py` | New - main wizard logic |
| `make.d/services.mk` | Modify - update `enable-service` target |
| `sietch/tests/test_enable_service.py` | New - test coverage |
| `.claude/CLAUDE.md` | Modify - document metadata format |
| `.github/shared/scaffold-templates.md` | Modify - document metadata format |

## Example: Paperless with Optional AI

After implementation, `services-available/paperless-ngx.yml` could have:

```yaml
# description: Document management system
# optional-group: ai-features
# optional-group-prompt: Enable AI features (document analysis with Ollama)?
# optional-group-services: ollama, openwebui

services:
  paperless-ngx:
    # ... existing config ...
```

User flow:
```
$ make enable-service paperless-ngx
Enabling paperless-ngx...

Enable AI features (document analysis with Ollama)? [y/N]: y
  Enabling ollama...
  Rendered: env.template -> services-enabled/ollama.env

  Enabling openwebui...
  Rendered: env.template -> services-enabled/openwebui.env

Building scaffold for 'paperless-ngx'...
  Rendered: env.template -> services-enabled/paperless-ngx.env
```

## Execution Strategy

### Task Tracking

Use TaskCreate/TaskUpdate to track implementation progress with dependencies:

```
Task 1: Extend metadata parsing (services.py)
Task 2: Add YAML dependency parser (services.py) - blocked by Task 1
Task 3: Create enable_service.py wizard - blocked by Task 2
Task 4: Update Makefile integration - blocked by Task 3
Task 5: Add tests - blocked by Task 3
Task 6: Update documentation - blocked by Task 4
```

### Subagent Model Selection

| Task | Model | Rationale |
|------|-------|-----------|
| Task 1: Metadata parsing | **haiku** | Simple pattern matching extension to existing code |
| Task 2: YAML dependency parser | **haiku** | Straightforward YAML parsing, small scope |
| Task 3: Enable wizard | **sonnet** | Core logic, recursive flow, multiple components |
| Task 4: Makefile update | **haiku** | Small change, well-defined pattern |
| Task 5: Tests | **sonnet** | Multiple test cases, needs to understand wizard logic |
| Task 6: Documentation | **haiku** | Straightforward doc updates |

### Parallel Execution

**Phase A** (sequential - foundation):
- Task 1 → Task 2 (same file, must be sequential)

**Phase B** (parallel - after Task 2):
- Task 3 (wizard) can start

**Phase C** (parallel - after Task 3):
- Task 4 (Makefile) and Task 5 (tests) can run in parallel

**Phase D** (after Task 4):
- Task 6 (docs)

### Subagent Prompts

Each subagent receives:
1. Full context from this plan
2. Specific file paths and code snippets
3. Clear acceptance criteria
4. Reference to existing patterns in codebase

## Verification

After implementation:
1. Run `make test` - all tests pass
2. Test manual flow:
   ```bash
   make disable-service paperless-ngx  # if enabled
   make enable-service paperless-ngx   # should prompt for optional services
   ```
3. Verify dependency auto-enable works with a service that has external `depends_on`

## Open Questions

None - all clarified during planning.
