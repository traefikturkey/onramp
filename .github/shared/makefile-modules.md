# Makefile Modules: Modular Build System

OnRamp uses modular Makefiles in `make.d/` to organize Docker Compose, service lifecycle, backup, and utility commands. The root `Makefile` aggregates all modules dynamically.

## Structure

### Root Makefile Pattern

```makefile
# Root Makefile (excerpt)
include $(wildcard make.d/*.mk)  # Include all .mk files in make.d/
```

The root `Makefile` sets global variables and includes all modules, preventing duplication and enabling reuse.

### Module Files

| Module | Purpose |
|--------|---------|
| `services.mk` | Service enable/disable/start/stop/restart/update/attach |
| `sietch.mk` | Build sietch container, run Python tools (scaffold, backup, database) |
| `backup.mk` | Backup/restore configuration and databases |
| `database.mk` | MariaDB operations (dump, restore, init) |
| `cloudflare.mk` | Cloudflare DNS API operations |
| `install.mk` | Installation and setup (Docker, Compose, dependencies) |
| `cleanup.mk` | Clean up containers, volumes, orphans |
| `utils.mk` | Utility commands (logs, editor, help) |
| `help.mk` | Help text and documentation |

## Conventions

### PHONY Targets

Non-file targets are declared `.PHONY` to prevent Make from checking for files with those names:

```makefile
.PHONY: start-service down-service restart-service
start-service: enable-service build
    $(DOCKER_COMPOSE) $(SERVICE_FLAGS) up -d --force-recreate $(SERVICE_PASSED_DNCASED)
```

### Variable Expansion

Three assignment operators control variable scope and timing:

| Operator | Behavior | Use Case |
|----------|----------|----------|
| `:=` | Immediate expansion | Read at assignment time (commands, constants) |
| `?=` | Conditional assignment | Set only if undefined (allow overrides) |
| `=` | Deferred expansion | Expand at use time (parameterized targets) |

Example:
```makefile
export HOSTIP := $(shell ip route get 1.1.1.1 | grep -oP 'src \K\S+')  # Immediate
export PUID ?= $(shell id -u)                                            # Conditional
EMPTY_TARGETS = $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS)) # Deferred
```

### SERVICE_PASSED Variables

Service commands like `make start-service <name>` extract the service name from arguments:

```makefile
# Root Makefile
export SERVICE_PASSED_DNCASED := $(strip $(word 2,$(MAKECMDGOALS)))
export SERVICE_PASSED_UPCASED := $(strip $(subst -,_,$(shell echo $(SERVICE_PASSED_DNCASED) | tr a-z A-Z )))
```

- `SERVICE_PASSED_DNCASED` — Service name as-is (lowercase with dashes)
- `SERVICE_PASSED_UPCASED` — Service name converted to UPPER_SNAKE_CASE for env var lookups

Usage in modules:
```makefile
start-service:
    $(DOCKER_COMPOSE) $(SERVICE_FLAGS) up -d $(SERVICE_PASSED_DNCASED)
```

### Docker Compose Aggregation

Files are aggregated from multiple locations:

```makefile
export DOCKER_COMPOSE_FILES := $(wildcard services-enabled/*.yml) \
                               $(wildcard overrides-enabled/*.yml) \
                               $(wildcard docker-compose.*.yml)
export DOCKER_COMPOSE_FLAGS := -f docker-compose.yml $(foreach file, $(DOCKER_COMPOSE_FILES), -f $(file))
```

This allows `docker-compose` to process the root file plus all enabled services and overrides.

## Module Pattern

Each module follows a consistent structure:

```makefile
#########################################################
##
## <Module Name>
##
#########################################################

.PHONY: target1 target2

target1: ## Help text for target1
    @echo "Executing target1..."
    $(COMMAND)

target2: ## Help text for target2
    $(COMMAND)
```

## Key Features

### Help Text

Targets include `##` comments for automatic help generation:

```makefile
start: build ## Start all services
    $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --remove-orphans
```

Tools parse `##` to build help output:
```bash
$ make help
start               Start all services
...
```

### Dependency Chains

Targets can depend on other targets:

```makefile
start-service: enable-service build
    $(DOCKER_COMPOSE) $(SERVICE_FLAGS) up -d --force-recreate $(SERVICE_PASSED_DNCASED)
```

`start-service` runs `enable-service` and `build` first.

### Silent Output Control

Commands are prefixed with `@` to suppress echoing:

```makefile
@echo "Enabling $(SERVICE_PASSED_DNCASED)..."  # Prints message, doesn't echo command
```

Commands without `@` show their execution in stdout.

## Common Patterns

### File Targets

Some targets represent actual files (symlinks, configs):

```makefile
services-enabled/$(SERVICE_PASSED_DNCASED).yml:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
    @echo "Enabling $(SERVICE_PASSED_DNCASED)..."
    @ln -s ../services-available/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true
else
    @echo "No such service file!"
endif
```

Make only runs this target if the file doesn't exist, enabling idempotent enables.

### Conditional Logic

Makefiles support conditionals for platform/environment detection:

```makefile
ifeq (, $(shell which docker-compose))
    DOCKER_COMPOSE := docker compose      # Newer docker (V2)
else
    DOCKER_COMPOSE := docker-compose      # Legacy
endif
```

### Error Handling

Prefix commands with `-` to ignore errors:

```makefile
down:
    -$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) down --remove-orphans
    -docker volume ls ... | xargs -r docker volume rm
```

Continues even if `down` fails (e.g., no containers running).

## Running Commands

```bash
make <target>                # Run a target
make <target> <service>      # Pass service name (sets SERVICE_PASSED_DNCASED)
make help                    # List all targets with help text
make <target> --dry-run      # Show what would run (GNU Make 4.3+)
```
