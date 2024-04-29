start-dev: COMPOSE_IGNORE_ORPHANS = true 
start-dev: build services-dev
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_DEVELOPMENT_FLAGS) up -d --force-recreate $(SERVICE_PASSED_DNCASED)

stop-dev:
	-$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_DEVELOPMENT_FLAGS) stop $(SERVICE_PASSED_DNCASED)

services-dev:
	mkdir -p ./services-dev