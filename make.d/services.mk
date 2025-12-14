#########################################################
##
## Service Operations
##
#########################################################

# Core service lifecycle
start-service: COMPOSE_IGNORE_ORPHANS = true
start-service: enable-service build
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) up -d --force-recreate $(SERVICE_PASSED_DNCASED)

down-service: stop-service
stop-service:
	-$(DOCKER_COMPOSE) $(SERVICE_FLAGS) stop $(SERVICE_PASSED_DNCASED)

restart-service: down-service start-service

attach-service:
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) exec $(SERVICE_PASSED_DNCASED) bash

update-service: down-service pull-service start-service
pull-service:
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) pull $(SERVICE_PASSED_DNCASED)

#########################################################
##
## Enable/Disable Services
##
#########################################################

.PHONY: enable-service build
enable-service: services-enabled/$(SERVICE_PASSED_DNCASED).yml

services-enabled/$(SERVICE_PASSED_DNCASED).yml:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
	@echo "Enabling $(SERVICE_PASSED_DNCASED)..."
	@ln -s ../services-available/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true
	@# Check if archived .env exists and prompt to restore
	@if $(SIETCH_RUN) python /scripts/services.py check-archive $(SERVICE_PASSED_DNCASED) 2>/dev/null | grep -q "yes"; then \
		echo ""; \
		echo "📦 Found archived .env file for $(SERVICE_PASSED_DNCASED)"; \
		$(SIETCH_RUN) python /scripts/services.py restore-env $(SERVICE_PASSED_DNCASED); \
	fi
	$(MAKE) scaffold-build $(SERVICE_PASSED_DNCASED)
else
	@echo "No such service file ./services-available/$(SERVICE_PASSED_DNCASED).yml!"
endif

enable-game: etc/$(SERVICE_PASSED_DNCASED)
ifneq (,$(wildcard ./services-available/games/$(SERVICE_PASSED_DNCASED).yml))
	@echo "Enabling $(SERVICE_PASSED_DNCASED)..."
	@ln -s ../services-available/games/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true
else
	@echo "No such game file ./services-available/games/$(SERVICE_PASSED_DNCASED).yml!"
endif

remove-game: disable-service
disable-game: disable-service
remove-service: disable-service

disable-service: stop-service ## Disable a service
	@# Archive .env file if it exists
	@if [ -f ./services-enabled/$(SERVICE_PASSED_DNCASED).env ]; then \
		echo "📦 Archiving $(SERVICE_PASSED_DNCASED).env..."; \
		$(SIETCH_RUN) python /scripts/services.py archive-env $(SERVICE_PASSED_DNCASED); \
	fi
	rm -f ./services-enabled/$(SERVICE_PASSED_DNCASED).yml
	rm -f ./overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml

nuke-service: disable-service ## Disable a service and remove its etc/ directory
	@if [ -d ./etc/$(SERVICE_PASSED_DNCASED) ]; then \
		echo "Removing ./etc/$(SERVICE_PASSED_DNCASED)..."; \
		rm -rf ./etc/$(SERVICE_PASSED_DNCASED); \
	fi

#########################################################
##
## Create/Edit Services
##
#########################################################

create-service: ## Create service from template
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./services-scaffold/_templates/service.template > ./services-available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/$(SERVICE_PASSED_DNCASED).yml

create-game: ## Create game service from template
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./services-scaffold/_templates/service.template > ./services-available/games/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/games/$(SERVICE_PASSED_DNCASED).yml

edit-service:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
	@$(EDITOR) services-available/$(SERVICE_PASSED_DNCASED).yml
else
	@echo "No such service file ./services-available/$(SERVICE_PASSED_DNCASED).yml!"
endif

generate-service-md:
	./.githooks/generate-services-markdown.sh

#########################################################
##
## Service Listing (Python-powered)
##
#########################################################

list-games: sietch-build ## List available games
	@$(SIETCH_RUN) python /scripts/services.py list --games

list-services: sietch-build ## List available services
	@$(SIETCH_RUN) python /scripts/services.py list --available

list-overrides: sietch-build ## List available overrides
	@$(SIETCH_RUN) python /scripts/services.py list --overrides

list-external: sietch-build ## List available external services
	@$(SIETCH_RUN) python /scripts/services.py list --external

list-enabled: sietch-build ## List enabled services
	@$(SIETCH_RUN) python /scripts/services.py list --enabled

print-enabled: list-enabled

count-enabled: sietch-build ## Count enabled services
	@echo "Total enabled services: $$($(SIETCH_RUN) python /scripts/services.py count --enabled)"

list-count: print-enabled count-enabled

#########################################################
##
## Overrides
##
#########################################################

enable-override: overrides-enabled/$(SERVICE_PASSED_DNCASED).yml
overrides-enabled/$(SERVICE_PASSED_DNCASED).yml:
	@ln -s ../overrides-available/$(SERVICE_PASSED_DNCASED).yml ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml || true

remove-override: disable-override
disable-override:
	rm -f ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml

#########################################################
##
## External Services (Traefik routing)
##
#########################################################

disable-external: ## Disable external service routing
	rm -f ./external-enabled/$(SERVICE_PASSED_DNCASED).yml

enable-external: ## Enable external service routing
	@mkdir -p ./etc/traefik/enabled
	@cp external-available/$(SERVICE_PASSED_DNCASED).yml ./external-enabled/$(SERVICE_PASSED_DNCASED).yml || true

create-external: ## Create external service from template
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./services-scaffold/_templates/external.template > ./external-available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./external-available/$(SERVICE_PASSED_DNCASED).yml

#########################################################
##
## Compose Operations
##
#########################################################

start-compose: COMPOSE_IGNORE_ORPHANS = true
start-compose: build
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) up -d --force-recreate

down-compose: stop-compose
stop-compose:
	-$(DOCKER_COMPOSE) $(SERVICE_FLAGS) stop

update-compose: down-compose pull-compose start-compose
pull-compose:
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) pull

compose-run:
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) run $(SERVICE_PASSED_DNCASED) $(second_arg)

#########################################################
##
## Development Mode
##
#########################################################

start-dev: COMPOSE_IGNORE_ORPHANS = true
start-dev: build services-dev
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_DEVELOPMENT_FLAGS) up -d --force-recreate $(SERVICE_PASSED_DNCASED)

stop-dev:
	-$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_DEVELOPMENT_FLAGS) stop $(SERVICE_PASSED_DNCASED)

services-dev:
	mkdir -p ./services-dev

#########################################################
##
## Service-Specific Commands
##
#########################################################

# Ollama
ifndef OLLAMA_CONTAINER_NAME
OLLAMA_CONTAINER_NAME=ollama
endif

ollama_cmd = @docker exec -it $(OLLAMA_CONTAINER_NAME) $(OLLAMA_CONTAINER_NAME)

pull-model: ## Pull ollama model
	$(ollama_cmd) pull $(first_arg)

update-ollama-models:
	$(shell pwd)/make.d/scripts/update-ollama-models.sh --docker
