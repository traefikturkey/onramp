#########################################################
##
## Sietch Container Commands
##
## The Sietch container provides Python-based tooling for:
## - Convention-based scaffolding (scaffold.py)
## - Environment migration from legacy .env or feature branch (migrate-env.py)
##
#########################################################

# Build Sietch container if needed (auto-rebuild if files change)
$(SIETCH_MARKER): $(SIETCH_FILES)
	@echo "Building Sietch container..."
	docker build -t $(SIETCH_IMAGE) ./sietch
	@touch $(SIETCH_MARKER)

sietch-build: $(SIETCH_MARKER) ## Build the Sietch tool container

sietch-rebuild: ## Force rebuild of Sietch container
	@echo "Force rebuilding Sietch container..."
	docker build --no-cache -t $(SIETCH_IMAGE) ./sietch
	@touch $(SIETCH_MARKER)

sietch-shell: sietch-build ## Open a shell in the Sietch container
	docker run --rm -it -v $(shell pwd):/app -u $(PUID):$(PGID) $(SIETCH_IMAGE) /bin/bash

sietch-test: ## Run dashboard unit tests
	@./sietch/run-tests.sh

sietch-test-cov: ## Run dashboard tests with coverage report
	@./sietch/run-tests.sh -v --cov=/dashboard --cov-report=term-missing

#########################################################
##
## Environment Migration
##
## Supports two migration paths:
## 1. Legacy master: .env -> services-enabled/*.env
## 2. Feature branch: environments-enabled/*.env -> services-enabled/*.env
##
#########################################################

# Migration runs automatically based on detected source
# Feature branch indicators: environments-available/*.template OR environments-enabled/*.env
# Legacy indicator: .env file at root
migrate-legacy-env: sietch-build
	@if [ ! -f services-enabled/.env ]; then \
		if [ -f .env ]; then \
			echo "Legacy .env detected. Migrating..."; \
			$(SIETCH_RUN) python /scripts/migrate-env.py; \
		elif [ -d environments-enabled ] || [ -d environments-available ]; then \
			echo "Feature branch detected. Migrating..."; \
			$(SIETCH_RUN) python /scripts/migrate-env.py; \
		fi \
	fi

migrate-env-dry-run: sietch-build ## Show what migration would do without making changes
	$(SIETCH_RUN) python /scripts/migrate-env.py --dry-run

migrate-env-force: sietch-build ## Force migration even if services-enabled/.env exists
	$(SIETCH_RUN) python /scripts/migrate-env.py --force

#########################################################
##
## Service Environment Migrations
##
## Handle breaking env var changes when container images are
## migrated to new versions with different configuration formats.
##
#########################################################

migrate-service-list: sietch-build ## List service env migrations and their status
	$(SIETCH_RUN) python /scripts/migrate_service_env.py list

migrate-service: sietch-build ## Migrate env vars for a service (e.g., make migrate-service samba)
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/migrate_service_env.py migrate $(SERVICE_PASSED_DNCASED)
else
	@echo "Usage: make migrate-service <service>"
	@echo "Example: make migrate-service samba"
	@echo ""
	@echo "Run 'make migrate-service-list' to see available migrations"
endif

migrate-service-all: sietch-build ## Run all pending service env migrations
	$(SIETCH_RUN) python /scripts/migrate_service_env.py migrate --all

migrate-service-dry-run: sietch-build ## Preview service env migration without changes
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/migrate_service_env.py migrate $(SERVICE_PASSED_DNCASED) --dry-run
else
	$(SIETCH_RUN) python /scripts/migrate_service_env.py migrate --all --dry-run
endif

migrate-service-check: sietch-build ## Check migration status for a service
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/migrate_service_env.py check $(SERVICE_PASSED_DNCASED)
else
	@echo "Usage: make migrate-service-check <service>"
endif

#########################################################
##
## Scaffold Commands
##
#########################################################

scaffold-list: sietch-build ## List available scaffolds
	$(SIETCH_RUN) python /scripts/scaffold.py list

scaffold-check: sietch-build ## Check if a service has scaffold files
	$(SIETCH_RUN) python /scripts/scaffold.py check $(SERVICE_PASSED_DNCASED)

scaffold-build: sietch-build ## Build scaffold for a service (e.g., make scaffold-build adguard)
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/scaffold.py build $(SERVICE_PASSED_DNCASED)
else
	@echo "Usage: make scaffold-build <service>"
	@echo "Example: make scaffold-build adguard"
endif

scaffold-build-all: sietch-build ## Build scaffolds for all enabled services
	$(SIETCH_RUN) python /scripts/scaffold.py build --all

scaffold-teardown: sietch-build ## Remove service env file (preserve etc/)
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/scaffold.py teardown $(SERVICE_PASSED_DNCASED)
else
	@echo "Usage: make scaffold-teardown <service>"
endif

scaffold-nuke: sietch-build ## Remove service env and etc/ directory
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/scaffold.py nuke $(SERVICE_PASSED_DNCASED)
else
	@echo "Usage: make scaffold-nuke <service>"
endif

create-scaffold-env: sietch-build ## Create env.template from compose file variables
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/extract_env.py $(SERVICE_PASSED_DNCASED)
	@echo ""
	@echo "Edit the generated template:"
	@echo "  $(EDITOR) services-scaffold/$(SERVICE_PASSED_DNCASED)/env.template"
else
	@echo "Usage: make create-scaffold-env <service>"
	@echo "Example: make create-scaffold-env gitea-runner"
endif

create-scaffold-env-dry-run: sietch-build ## Preview env.template without creating
ifdef SERVICE_PASSED_DNCASED
	$(SIETCH_RUN) python /scripts/extract_env.py $(SERVICE_PASSED_DNCASED) --dry-run
else
	@echo "Usage: make create-scaffold-env-dry-run <service>"
endif

#########################################################
##
## Environment File Commands
##
#########################################################

edit-env: ## Edit a service's environment file
ifdef SERVICE_PASSED_DNCASED
	@if [ -f services-enabled/$(SERVICE_PASSED_DNCASED).env ]; then \
		$(EDITOR) services-enabled/$(SERVICE_PASSED_DNCASED).env; \
	else \
		echo "No environment file found: services-enabled/$(SERVICE_PASSED_DNCASED).env"; \
		echo "Enable the service first with: make enable-service $(SERVICE_PASSED_DNCASED)"; \
	fi
else
	@echo "Usage: make edit-env <service>"
	@echo "Example: make edit-env adguard"
endif

edit-env-onramp: ## Edit the global OnRamp environment file
	@if [ -f services-enabled/.env ]; then \
		$(EDITOR) services-enabled/.env; \
	else \
		echo "Global environment file not found: services-enabled/.env"; \
		echo "Run 'make scaffold-build onramp' to create it from template"; \
	fi

edit-env-nfs: ## Edit the NFS environment file
	@if [ -f services-enabled/.env.nfs ]; then \
		$(EDITOR) services-enabled/.env.nfs; \
	else \
		echo "NFS environment file not found: services-enabled/.env.nfs"; \
		echo "Run 'make scaffold-build onramp' to create it from template"; \
	fi

edit-env-external: ## Edit the external services environment file
	@if [ -f services-enabled/.env.external ]; then \
		$(EDITOR) services-enabled/.env.external; \
	else \
		echo "External environment file not found: services-enabled/.env.external"; \
		echo "Run 'make scaffold-build onramp' to create it from template"; \
	fi

edit-env-custom: ## Edit custom/unmapped variables file
	$(EDITOR) services-enabled/custom.env

#########################################################
##
## Testing Commands
##
#########################################################

test: sietch-build ## Run unit tests locally with uv
	cd sietch && uv run pytest

test-coverage: sietch-build ## Run tests with coverage report
	cd sietch && uv run pytest --cov=scripts --cov-report=html

test-docker: sietch-build ## Run tests inside the Sietch container
	docker run --rm -v $(shell pwd)/sietch:/app -w /app $(SIETCH_IMAGE) sh -c "uv sync --all-extras && uv run pytest"

#$(info "sietch.mk loaded")
