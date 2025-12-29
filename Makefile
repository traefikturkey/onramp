# Files Make can safely include (only main .env - no shell variable syntax)
# Note: .env.nfs, .env.external, and *.env files use shell variable syntax
# (e.g., ${VAR:-default}) that Make interprets as recursive references.
MAKE_INCLUDE_FILES := $(wildcard ./services-enabled/.env)

# All env files for docker-compose: .env, .env.*, and *.env
# Order matters: later files override earlier ones
# These are loaded via --env-file for YAML variable substitution
# Note: env_file: in YAML only provides runtime container environment
ENV_FILES := $(wildcard ./services-enabled/.env) $(wildcard ./services-enabled/.env.*) $(wildcard ./services-enabled/*.env)
ENV_FLAGS := $(foreach file, $(ENV_FILES), --env-file $(file))

# Global env files only (for sietch container - avoids malformed service .env files breaking all operations)
GLOBAL_ENV_FILES := $(wildcard ./services-enabled/.env) $(wildcard ./services-enabled/.env.*)
GLOBAL_ENV_FLAGS := $(foreach file, $(GLOBAL_ENV_FILES), --env-file $(file))

ifneq (,$(MAKE_INCLUDE_FILES))
    include $(MAKE_INCLUDE_FILES)
    export
endif

# Fallback: include legacy .env if it exists (migration pending)
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# look for the second target word passed to make
export SERVICE_PASSED_DNCASED := $(strip $(word 2,$(MAKECMDGOALS)))
export SERVICE_PASSED_UPCASED := $(strip $(subst -,_,$(shell echo '$(SERVICE_PASSED_DNCASED)' | tr a-z A-Z )))

export DOCKER_COMPOSE_FILES :=  $(wildcard services-enabled/*.yml) $(wildcard overrides-enabled/*.yml) $(wildcard docker-compose.*.yml)
export DOCKER_COMPOSE_FLAGS := $(ENV_FLAGS) -f docker-compose.yml $(foreach file, $(DOCKER_COMPOSE_FILES), -f $(file))

DOCKER_COMPOSE_DEVELOPMENT_FILES := $(wildcard services-dev/*.yml)
DOCKER_COMPOSE_DEVELOPMENT_FLAGS := --project-directory ./ $(foreach file, $(DOCKER_COMPOSE_DEVELOPMENT_FILES), -f $(file))

# For single-service commands
SERVICE_FILES := $(wildcard services-enabled/$(SERVICE_PASSED_DNCASED).yml) $(wildcard overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml)
SERVICE_FLAGS := $(ENV_FLAGS) --project-directory ./ $(foreach file, $(SERVICE_FILES), -f $(file))

# get the boxes ip address and the current users id and group id
export HOSTIP := $(shell ip route get 1.1.1.1 | grep -oP 'src \K\S+')
export PUID 	:= $(shell id -u)
export PGID 	:= $(shell id -g)
export HOST_NAME := $(or $(HOST_NAME), $(shell hostname))
export CF_RESOLVER_WAITTIME := $(strip $(or $(CF_RESOLVER_WAITTIME), 60))

# Prefer 'docker compose' (plugin) over 'docker-compose' (standalone)
# The standalone binary may be outdated and have bugs with many --env-file flags
ifeq (0, $(shell docker compose version >/dev/null 2>&1; echo $$?))
	DOCKER_COMPOSE := docker compose
else
	DOCKER_COMPOSE := docker-compose
endif

# setup PLEX_ALLOWED_NETWORKS defaults if they are not already in the .env file
ifndef PLEX_ALLOWED_NETWORKS
	export PLEX_ALLOWED_NETWORKS := $(HOSTIP/24)
endif

# check what editor is available
ifdef VSCODE_REMOTE_SSH
	EDITOR := $(EDITOR)
else ifdef VSCODE_IPC_HOOK_CLI
	EDITOR := code
else ifdef EDITOR
	EDITOR := $(EDITOR)
else
	EDITOR := vim
endif

# Sietch container configuration
SIETCH_IMAGE := sietch
SIETCH_MARKER := sietch/.built
SIETCH_FILES := $(shell find sietch/ -type f ! -name '.built' \
	! -path 'sietch/.venv/*' \
	! -path 'sietch/__pycache__/*' \
	! -path 'sietch/*/__pycache__/*' \
	! -path 'sietch/.pytest_cache/*' \
	! -path 'sietch/.coverage' \
	! -name '*.pyc' \
	2>/dev/null)
SIETCH_COMPUTED_VARS := -e HOSTIP=$(HOSTIP) -e PUID=$(PUID) -e PGID=$(PGID) -e HOST_NAME=$(HOST_NAME) -e TZ=$(TZ) -e HOST_DOMAIN=$(HOST_DOMAIN)
SIETCH_RUN := docker run --rm $(GLOBAL_ENV_FLAGS) $(SIETCH_COMPUTED_VARS) -v $(shell pwd):/app -v /var/run/docker.sock:/var/run/docker.sock --network traefik -u $(PUID):$(PGID) $(SIETCH_IMAGE)

# prevents circular references, do not remove
BUILD_DEPENDENCIES :=

# use the rest as arguments as empty targets aka: MAGIC
EMPTY_TARGETS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(EMPTY_TARGETS):;@:)

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
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) pull --ignore-pull-failures

logs: ## show logs for a service or all services if no service is passed
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) logs -f $(SERVICE_PASSED_DNCASED)

restart: down start ## restart all services that are enabled

update: down pull start ## update all the services that are enabled and restart them

# Include all Makefiles in make.d directory
include $(wildcard make.d/*.mk)
