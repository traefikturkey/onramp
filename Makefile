# include .env variable in the current environment
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

export DOCKER_COMPOSE_FILES :=  $(wildcard services-enabled/*.yml) $(wildcard overrides-enabled/*.yml) $(wildcard docker-compose.*.yml) 
export DOCKER_COMPOSE_FLAGS := -f docker-compose.yml $(foreach file, $(DOCKER_COMPOSE_FILES), -f $(file))

# look for the second target word passed to make
export SERVICE_PASSED_DNCASED := $(strip $(word 2,$(MAKECMDGOALS)))
export SERVICE_PASSED_UPCASED := $(strip $(subst -,_,$(shell echo $(SERVICE_PASSED_DNCASED) | tr a-z A-Z )))

# get the boxes ip address and the current users id and group id
export HOSTIP := $(shell ip route get 1.1.1.1 | grep -oP 'src \K\S+')
export PUID 	:= $(shell id -u)
export PGID 	:= $(shell id -g)
export HOST_NAME := $(or $(HOST_NAME), $(shell hostname))

# check if we should use docker-compose or docker compose
ifeq (, $(shell which docker-compose))
	DOCKER_COMPOSE := docker compose
else
	DOCKER_COMPOSE := docker-compose
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

# used to look for the file in the services-enabled folder when [start|stop|pull]-service is used 
SERVICE_FILES := $(wildcard services-enabled/$(SERVICE_PASSED_DNCASED).yml) $(wildcard overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml)
SERVICE_FLAGS := --project-directory ./ $(foreach file, $(SERVICE_FILES), -f $(file))

# use the rest as arguments as empty targets aka: MAGIC
EMPTY_TARGETS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(EMPTY_TARGETS):;@:)

# this is the default target run if no other targets are passed to make
# i.e. if you just type: make
start: build
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d
	
remove-orphans: build
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --remove-orphans	

up: build
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up --force-recreate --remove-orphans --abort-on-container-exit

down: 
	-$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) down --remove-orphans
	-docker volume ls --quiet --filter "label=remove_volume_on=down" | xargs -r docker volume rm 

pull:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) pull

logs:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) logs -f

restart: down start

update: down pull start

bash-run:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) run -it --rm $(SERVICE_PASSED_DNCASED) sh

bash-exec:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) exec $(SERVICE_PASSED_DNCASED) sh

#########################################################
#
# service commands
#
#########################################################

start-service: COMPOSE_IGNORE_ORPHANS = true 
start-service: build enable-service
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) up -d --force-recreate $(SERVICE_PASSED_DNCASED)

down-service: stop-service
stop-service: 
	-$(DOCKER_COMPOSE) $(SERVICE_FLAGS) stop $(SERVICE_PASSED_DNCASED)

restart-service: down-service start-service

update-service: down-service pull-service start-service
pull-service: 
	$(DOCKER_COMPOSE) $(SERVICE_FLAGS) pull $(SERVICE_PASSED_DNCASED)

enable-game: etc/$(SERVICE_PASSED_DNCASED)
	@ln -s ../services-available/games/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true

enable-service: etc/$(SERVICE_PASSED_DNCASED) services-enabled/$(SERVICE_PASSED_DNCASED).yml

etc/$(SERVICE_PASSED_DNCASED):
	@mkdir -p ./etc/$(SERVICE_PASSED_DNCASED)

services-enabled/$(SERVICE_PASSED_DNCASED).yml:
	@ln -s ../services-available/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true

remove-game: disable-service
disable-game: disable-service
remove-service: disable-service
disable-service: stop-service
	rm ./services-enabled/$(SERVICE_PASSED_DNCASED).yml
	rm ./overrides-enabled/$(SERVICE_PASSED_DNCASED)-*.yml 2> /dev/null || true

create-service:
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/service.template > ./services-available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/$(SERVICE_PASSED_DNCASED).yml

create-game:
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/service.template > ./services-available/games/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./services-available/games/$(SERVICE_PASSED_DNCASED).yml

#########################################################
#
# compose commands
#
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

#########################################################
#
# staging commands
#
#########################################################

start-staging: build
	ACME_CASERVER=https://acme-staging-v02.api.letsencrypt.org/directory $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --force-recreate
	@echo "waiting 30 seconds for cert DNS propogation..."
	@sleep 30
	@echo "open https://$(HOST_NAME).$(HOST_DOMAIN)/traefik in a browser"
	@echo "and check that you have a staging cert from LetsEncrypt!"
	@echo ""
	@echo "if you don't get the write cert run the following command and look for error messages:"
	@echo "$(DOCKER_COMPOSE) logs | grep acme"
	@echo ""
	@echo "otherwise run the following command if you successfully got a staging certificate:"
	@echo "make down-staging"

down-staging:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) down
	$(MAKE) clean-acme

#########################################################
#
# list commands
#
#########################################################

list-games:
	@ls -1 ./services-available/games | sed -n 's/\.yml$ //p'

list-services:
	@ls -1 ./services-available/ | sed -e 's/\.yml$ //'

list-overrides:
	@ls -1 ./overrides-available/ | sed -e 's/\.yml$ //'

list-external:
	@ls -1 ./etc/traefik/available/ | sed -e 's/\.yml$ //'

#########################################################
#
# build related commands
#
#########################################################

build: .env etc/authelia/configuration.yml etc/dashy/dashy-config.yml etc/prometheus/conf 

.env:
	cp .templates/env.template .env
	$(EDITOR) .env

etc/authelia/configuration.yml:
	envsubst '$${HOST_DOMAIN}' < ./etc/authelia/configuration.template > ./etc/authelia/configuration.yml

etc/dashy/dashy-config.yml:
	mkdir -p ./etc/dashy
	touch ./etc/dashy/dashy-config.yml

etc/prometheus/conf:
	mkdir -p etc/prometheus/conf
	cp --no-clobber --recursive	etc/prometheus/conf-originals/* etc/prometheus/conf

#########################################################
#
# override commands
#
#########################################################

enable-override: overrides-enabled/$(SERVICE_PASSED_DNCASED).yml
overrides-enabled/$(SERVICE_PASSED_DNCASED).yml:
	@ln -s ../overrides-available/$(SERVICE_PASSED_DNCASED).yml ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml || true

remove-override: disable-override
disable-override:
	rm ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml 

#########################################################
#
# external commands
#
#########################################################

disable-external:
	rm ./etc/traefik/enabled/$(SERVICE_PASSED_DNCASED).yml

enable-external:
	@cp ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml ./etc/traefik/enabled/$(SERVICE_PASSED_DNCASED).yml || true

create-external:
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/external.template > ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml

#########################################################
#
# helper commands
#
#########################################################

edit-env:
	$(EDITOR) .env

install-node-exporter:
	curl -s https://gist.githubusercontent.com/ilude/2cf7a3b7712378c6b9bcf1e1585bf70f/raw/setup_node_exporter.sh?$(date +%s) | /bin/bash -s | tee build.log

#########################################################
#
# backup and restore up commands
#
#########################################################

export-backup: create-backup
	@echo "export-backup is depercated and will be removed in the future, please use make create-backup"

import-backup: restore-backup
	@echo "import-backup is depercated and will be removed in the future, please use make restore-backup"

create-backup: backups
	sudo tar --exclude=.keep -cvzf ./backups/traefik-config-backup.tar.gz ./etc ./services-enabled ./overrides-enabled .env || true

backups:
	mkdir -p ./backups/

restore-backup:
	sudo tar -xvf ./backups/traefik-config-backup.tar.gz

#########################################################
#
# clean up commands
#
#########################################################

clean-acme:
	@echo "removing acme certificate file"
	sudo rm etc/traefik/letsencrypt/acme.json

remove-etc: 
	rm -rf ./etc/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/

reset-database-folder:
	rm -rf ./media/databases/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/
	git checkout ./media/databases/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/.keep

reset-etc: remove-etc
	git checkout ./etc/$(or $(SERVICE_PASSED_DNCASED),no_service_passed)/*

reset-database: remove-etc reset-database-folder	

#########################################################
#
# cloudflare tunnel commands
#
#########################################################

cloudflare-login:
	$(DOCKER_COMPOSE) run --rm cloudflared login

create-tunnel:
	$(DOCKER_COMPOSE) run --rm cloudflared tunnel create $(CLOUDFLARE_TUNNEL_NAME)
	$(DOCKER_COMPOSE) run --rm cloudflared tunnel route dns $(CLOUDFLARE_TUNNEL_NAME) $(CLOUDFLARE_TUNNEL_HOSTNAME)

delete-tunnel:
	$(DOCKER_COMPOSE) run --rm cloudflared tunnel cleanup $(CLOUDFLARE_TUNNEL_NAME)
	$(DOCKER_COMPOSE) run --rm cloudflared tunnel delete $(CLOUDFLARE_TUNNEL_NAME)

show-tunnel:
	$(DOCKER_COMPOSE) run --rm cloudflared tunnel info $(CLOUDFLARE_TUNNEL_NAME)

#########################################################
#
# test and debugging commands
#
#########################################################

excuse:
	@curl -s programmingexcuses.com | egrep -o "<a[^<>]+>[^<>]+</a>" | egrep -o "[^<>]+" | sed -n 2p

test-smtp:
	envsubst .templates/smtp.template | nc localhost 25

# https://stackoverflow.com/questions/7117978/gnu-make-list-the-values-of-all-variables-or-macros-in-a-particular-run
echo:
	@$(MAKE) -pn | grep -A1 "^# makefile"| grep -v "^#\|^--" | grep -e "^[A-Z]+*" | sort

env:
	@env | sort

include env_ifs.mk