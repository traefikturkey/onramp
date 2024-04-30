
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
	# here's where the magic happens
	# Searches for volume paths in the Docker Compose file associated with the specified service. 
	# It extracts paths starting with `./etc/` followed by the service name and checks if they 
	# have an extension. If a path without a forward slash (`/`) and with an extension is found, 
	# it creates the corresponding directory. 
	@grep -oE "\./etc/$(SERVICE_PASSED_DNCASED)\S*" services-enabled/$(SERVICE_PASSED_DNCASED).yml | sed 's/:.*//' | while read -r volume; do \
		if [[ "$$volume" == *.* ]]; then \
			mkdir -p "$$(dirname "$$volume")"; \
			touch "$$volume"; \
		else \
			mkdir -p "$$volume"; \
		fi \
	done
	@sleep 1
else
	@echo "No such service file ./services-available/$(SERVICE_PASSED_DNCASED).yml!"
endif

remove-game: disable-service ## Disable a game and disable it before removing it
disable-game: disable-service ## Disable a game
remove-service: disable-service ## Disable a service and disable it before removing it
disable-service: stop-service ## Disable a service
	rm ./services-enabled/$(SERVICE_PASSED_DNCASED).yml
	rm ./overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml 2> /dev/null || true

create-service: ## create a service file from the template and open it in the editor 
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/service.template > ./services-available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/$(SERVICE_PASSED_DNCASED).yml

create-game: ## create a game service using the service template and open it in the editor
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/service.template > ./services-available/games/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/games/$(SERVICE_PASSED_DNCASED).yml