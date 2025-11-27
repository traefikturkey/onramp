#########################################################
##
## Sietch Container Commands
##
## The Sietch container provides Python-based tooling for:
## - Convention-based scaffolding (scaffold.py)
## - Legacy .env migration (migrate-env.py)
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

#########################################################
##
## Legacy .env Migration
##
#########################################################

# Migration runs automatically if .env exists and services-enabled/.env doesn't
migrate-legacy-env: sietch-build
	@if [ -f .env ] && [ ! -f services-enabled/.env ]; then \
		echo "Legacy .env detected. Migrating..."; \
		$(SIETCH_RUN) python /scripts/migrate-env.py; \
	fi

migrate-env-dry-run: sietch-build ## Show what migration would do without making changes
	$(SIETCH_RUN) python /scripts/migrate-env.py --dry-run

migrate-env-force: sietch-build ## Force migration even if services-enabled/.env exists
	$(SIETCH_RUN) python /scripts/migrate-env.py --force

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

#$(info "sietch.mk loaded")
