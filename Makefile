# include .env variable in the current environment
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# look for the second target word passed to make
export SERVICE_PASSED_DNCASED := $(strip $(word 2,$(MAKECMDGOALS)))
export SERVICE_PASSED_UPCASED := $(strip $(subst -,_,$(shell echo $(SERVICE_PASSED_DNCASED) | tr a-z A-Z )))

export DOCKER_COMPOSE_FILES :=  $(wildcard services-enabled/*.yml) $(wildcard overrides-enabled/*.yml) $(wildcard docker-compose.*.yml) 
export DOCKER_COMPOSE_FLAGS := -f docker-compose.yml $(foreach file, $(DOCKER_COMPOSE_FILES), -f $(file))

DOCKER_COMPOSE_DEVELOPMENT_FILES := $(wildcard services-dev/*.yml)
DOCKER_COMPOSE_DEVELOPMENT_FLAGS := --project-directory ./ $(foreach file, $(DOCKER_COMPOSE_DEVELOPMENT_FILES), -f $(file))

# used to look for the file in the services-enabled folder when [start|stop|pull]-service is used 
SERVICE_FILES := $(wildcard services-enabled/$(SERVICE_PASSED_DNCASED).yml) $(wildcard overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml)
SERVICE_FLAGS := --project-directory ./ $(foreach file, $(SERVICE_FILES), -f $(file))

# get the boxes ip address and the current users id and group id
export HOSTIP := $(shell ip route get 1.1.1.1 | grep -oP 'src \K\S+')
export PUID 	:= $(shell id -u)
export PGID 	:= $(shell id -g)
export HOST_NAME := $(or $(HOST_NAME), $(shell hostname))
export CF_RESOLVER_WAITTIME := $(strip $(or $(CF_RESOLVER_WAITTIME), 60))

# check if we should use docker-compose or docker compose
ifeq (, $(shell which docker-compose))
	DOCKER_COMPOSE := docker compose
else
	DOCKER_COMPOSE := docker-compose
endif

ifneq (,$(wildcard ./services-enabled/cloudflare-tunnel.yml))
	BUILD_DEPENDENCIES += cloudflare-tunnel
	include make.d/cloudflare.mk
endif

# setup PLEX_ALLOWED_NETWORKS defaults if they are not already in the .env file
ifndef PLEX_ALLOWED_NETWORKS
	export PLEX_ALLOWED_NETWORKS := $(HOSTIP/24)
endif

# check what editor is available
ifdef VSCODE_IPC_HOOK_CLI
	EDITOR := code
else
	EDITOR := nano
endif

# use the rest as arguments as empty targets aka: MAGIC
EMPTY_TARGETS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(EMPTY_TARGETS):;@:)

# Include all Makefiles in make.d directory
include $(wildcard make.d/*.mk)

#########################################################
##
## basic commands
##
#########################################################

# this is the default target run if no other targets are passed to make
# i.e. if you just type: make
start: build
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --remove-orphans
	
remove-orphans: build
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --remove-orphans	

up: build
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up --force-recreate --remove-orphans --abort-on-container-exit

down: ## stop all services and remove all containers and networks
	-$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) down --remove-orphans
	-docker volume ls --quiet --filter "label=remove_volume_on=down" | xargs -r docker volume rm 

pull:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) pull

logs: ## show logs for a service or all services if no service is passed
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) logs -f $(SERVICE_PASSED_DNCASED)

restart: down start ## restart all services that are enabled

update: down pull start ## update all the services that are enabled and restart them



