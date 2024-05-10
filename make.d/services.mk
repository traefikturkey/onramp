
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
enable-service: etc/$(SERVICE_PASSED_DNCASED) services-enabled/$(SERVICE_PASSED_DNCASED).yml environments-enabled/$(SERVICE_PASSED_DNCASED).env ## Enable a service by creating a symlink to the service file in the services-enabled folder

etc/$(SERVICE_PASSED_DNCASED):
	@mkdir -p ./etc/$(SERVICE_PASSED_DNCASED)

services-enabled/$(SERVICE_PASSED_DNCASED).yml:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
	@echo "Enabling $(SERVICE_PASSED_DNCASED)..."
	@ln -s ../services-available/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true

#   Need to look if this can enhance the scaffolding setup. 
#	@./make.d/scripts/create-etc-volumes.sh $(SERVICE_PASSED_DNCASED)
else
	@echo "No such service file ./services-available/$(SERVICE_PASSED_DNCASED).yml!"
endif
ifneq (,$(wildcard ./services-scaffold/$(SERVICE_PASSED_DNCASED)/build-up.sh))
	make scaffold-build-up $(SERVICE_PASSED_DNCASED)
	@sleep 1
endif

environments-enabled/$(SERVICE_PASSED_DNCASED).env:
ifeq (,$(wildcard ./environments-available/$(SERVICE_PASSED_DNCASED).template))
	@envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/environment.template > environments-available/$(SERVICE_PASSED_DNCASED).template
endif
	@python3 scripts/env-subst.py environments-available/$(SERVICE_PASSED_DNCASED).template $(SERVICE_PASSED_UPCASED)

remove-game: disable-service ## Disable a game and disable it before removing it
disable-game: disable-service ## Disable a game
remove-service: disable-service ## Disable a service and disable it before removing it
disable-service: stop-service ## Disable a service
	rm ./environments-enabled/$(SERVICE_PASSED_DNCASED).env
	rm ./services-enabled/$(SERVICE_PASSED_DNCASED).yml
	rm ./overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml 2> /dev/null || true
nuke-service: disable-service scaffold-tear-down

create-service: ## create a service file from the template and open it in the editor 
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/service.template > ./services-available/$(SERVICE_PASSED_DNCASED).yml
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/environment.template > environments-available/$(SERVICE_PASSED_DNCASED).template
	$(EDITOR) ./services-available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) environments-available/$(SERVICE_PASSED_DNCASED).template

create-game: ## create a game service using the service template and open it in the editor
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/service.template > ./services-available/games/$(SERVICE_PASSED_DNCASED).yml
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/environment.template > environments-available/$(SERVICE_PASSED_DNCASED).template
	$(EDITOR) ./services-available/games/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) environments-available/$(SERVICE_PASSED_DNCASED).template
