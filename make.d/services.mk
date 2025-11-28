#########################################################
##
## service commands
##
#########################################################

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

enable-game: etc/$(SERVICE_PASSED_DNCASED)
ifneq (,$(wildcard ./services-available/games/$(SERVICE_PASSED_DNCASED).yml))
	@echo "Enabling $(SERVICE_PASSED_DNCASED)..."
	@ln -s ../services-available/games/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true
else
	@echo "No such game file ./services-available/games/$(SERVICE_PASSED_DNCASED).yml!"
endif

.PHONY: enable-service build
enable-service: services-enabled/$(SERVICE_PASSED_DNCASED).yml ## Enable a service by creating a symlink to the service file in the services-enabled folder

services-enabled/$(SERVICE_PASSED_DNCASED).yml:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
	@echo "Enabling $(SERVICE_PASSED_DNCASED)..."
	@ln -s ../services-available/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true
	@./make.d/scripts/create-etc-volumes.sh $(SERVICE_PASSED_DNCASED)
	@# Run scaffold if templates exist for this service
	@if [ -d services-scaffold/$(SERVICE_PASSED_DNCASED) ]; then \
		echo "Running scaffold for $(SERVICE_PASSED_DNCASED)..."; \
		$(MAKE) scaffold-build $(SERVICE_PASSED_DNCASED); \
	fi
else
	@echo "No such service file ./services-available/$(SERVICE_PASSED_DNCASED).yml!"
endif

remove-game: disable-service ## Disable a game and disable it before removing it
disable-game: disable-service ## Disable a game
remove-service: disable-service ## Disable a service and disable it before removing it

disable-service: stop-service ## Disable a service
	rm -f ./services-enabled/$(SERVICE_PASSED_DNCASED).yml
	rm -f ./services-enabled/$(SERVICE_PASSED_DNCASED).env
	rm -f ./overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml

nuke-service: disable-service ## Disable a service and remove its etc/ directory
	@if [ -d ./etc/$(SERVICE_PASSED_DNCASED) ]; then \
		echo "Removing ./etc/$(SERVICE_PASSED_DNCASED)..."; \
		rm -rf ./etc/$(SERVICE_PASSED_DNCASED); \
	fi

create-service: ## create a service file from the template and open it in the editor
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./make.d/templates/service.template > ./services-available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/$(SERVICE_PASSED_DNCASED).yml

create-game: ## create a game service using the service template and open it in the editor
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./make.d/templates/service.template > ./services-available/games/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/games/$(SERVICE_PASSED_DNCASED).yml

edit-service:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
	@$(EDITOR) services-available/$(SERVICE_PASSED_DNCASED).yml
else
	@echo "No such service file ./services-available/$(SERVICE_PASSED_DNCASED).yml!"
endif

generate-service-md:
	./.githooks/generate-services-markdown.sh
