# include .env variable in the current environment
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# any disabled-*.yml docker-compose files will be ignored
disabled_files := $(wildcard services-enabled/disabled-*.yml)
# all other *.yml files in the current directory will be included 
# when running make commands that call docker compose
compose_files := $(filter-out $(disabled_files), $(wildcard services-enabled/*.yml)) 
args := -f docker-compose.yml $(foreach file, $(compose_files), -f $(file))


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

# check what editor is available
ifeq (, $(shell which code))
	EDITOR := code
else
	EDITOR := nano
endif

# look for the second target word passed to make
export PASSED_SERVICE := $(word 2,$(MAKECMDGOALS))
export ETC_SERVICE := $(subst nfs-,,$(PASSED_SERVICE))

# used to look for the file in the services-enabled folder when [start|stop|pull]-service is used  
SERVICE_FILE = --project-directory ./ -f ./services-enabled/$(PASSED_SERVICE).yml

# use the rest as arguments as empty targets aka: MAGIC
EMPTY_TARGETS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
$(eval $(EMPTY_TARGETS):;@:)

# this is the default target run if no other targets are passed to make
# i.e. if you just type: make
start: build
	$(DOCKER_COMPOSE) $(args) up -d
	
remove-orphans: build
	$(DOCKER_COMPOSE) $(args) up -d --remove-orphans	

up: build
	$(DOCKER_COMPOSE) $(args) up --force-recreate --remove-orphans --abort-on-container-exit

down: 
	-$(DOCKER_COMPOSE) $(args) down --remove-orphans
	-docker volume ls --quiet --filter "label=remove_volume_on=down" | xargs -r docker volume rm

start-service: COMPOSE_IGNORE_ORPHANS = true 
start-service: build enable-service
	$(DOCKER_COMPOSE) $(SERVICE_FILE) up -d --force-recreate $(PASSED_SERVICE)

start-compose: COMPOSE_IGNORE_ORPHANS = true 
start-compose: build 
	$(DOCKER_COMPOSE) $(SERVICE_FILE) up -d --force-recreate

down-service: 
	-$(DOCKER_COMPOSE) $(SERVICE_FILE) stop $(PASSED_SERVICE)

down-compose: 
	-$(DOCKER_COMPOSE) $(SERVICE_FILE) stop

pull-service: 
	$(DOCKER_COMPOSE) $(SERVICE_FILE) pull $(PASSED_SERVICE)

pull-compose: 
	$(DOCKER_COMPOSE) $(SERVICE_FILE) pull

stop-service: down-service

restart-service: down-service build start-service

update-service: down-service build pull-service start-service

start-staging: build
	ACME_CASERVER=https://acme-staging-v02.api.letsencrypt.org/directory $(DOCKER_COMPOSE) $(args) up -d --force-recreate
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
	$(DOCKER_COMPOSE) $(args) down
	$(MAKE) clean-acme

clean-acme:
	@echo "cleaning up staging certificates"
	sudo rm etc/traefik/letsencrypt/acme.json

pull:
	$(DOCKER_COMPOSE) $(args) pull

logs:
	$(DOCKER_COMPOSE) $(args) logs -f

restart: down start

update: down pull start

exec:
	$(DOCKER_COMPOSE) $(args) exec $(PASSED_SERVICE) sh

build: .env etc/prometheus/conf etc/authelia/configuration.yml

etc/authelia/configuration.yml:
	envsubst '$${HOST_DOMAIN}' < ./etc/authelia/configuration.template > ./etc/authelia/configuration.yml

.env:
	cp .env.sample .env
	$(EDITOR) .env

etc/prometheus/conf:
	mkdir -p etc/prometheus/conf
	cp --no-clobber --recursive	etc/prometheus/conf-originals/* etc/prometheus/conf

list-games:
	@ls -1 ./services-available/games | sed -n 's/\.yml$ //p'

list-services:
	@ls -1 ./services-available/ | sed -e 's/\.yml$ //'

list-external:
	@ls -1 ./etc/traefik/available/ | sed -e 's/\.yml$ //'

etc/$(ETC_SERVICE):
	@mkdir -p ./etc/$(ETC_SERVICE)

enable-game: etc/$(ETC_SERVICE)
	@ln -s ../services-available/games/$(PASSED_SERVICE).yml ./services-enabled/$(PASSED_SERVICE).yml || true

enable-service: etc/$(PASSED_SERVICE) services-enabled/$(PASSED_SERVICE).yml

services-enabled/$(PASSED_SERVICE).yml:
	@ln -s ../services-available/$(PASSED_SERVICE).yml ./services-enabled/$(PASSED_SERVICE).yml || true

enable-game-copy: etc/$(PASSED_SERVICE)
	@cp ./services-available/games/$(PASSED_SERVICE).yml ./services-enabled/$(PASSED_SERVICE).yml || true

enable-service-copy: etc/$(PASSED_SERVICE)
	@cp ./services-available/$(PASSED_SERVICE).yml ./services-enabled/$(PASSED_SERVICE).yml || true

enable-external:
	@cp ./etc/traefik/available/$(PASSED_SERVICE).yml ./etc/traefik/enabled/$(PASSED_SERVICE).yml || true

disable-game: disable-service

disable-service:
	rm ./services-enabled/$(PASSED_SERVICE).yml

disable-external:
	rm ./etc/traefik/enabled/$(PASSED_SERVICE).yml

create-service:
	envsubst '$${PASSED_SERVICE}' < ./services-available/.service.template > ./services-available/$(PASSED_SERVICE).yml

create-game:
	envsubst '$${PASSED_SERVICE}' < ./services-available/.service.template > ./services-available/games/$(PASSED_SERVICE).yml

install-node-exporter:
	curl -s https://gist.githubusercontent.com/ilude/2cf7a3b7712378c6b9bcf1e1585bf70f/raw/setup_node_exporter.sh?$(date +%s) | /bin/bash -s | tee build.log

export-backup:
	sudo tar -cvzf traefik-config-backup.tar.gz ./etc ./services-enabled .env || true

import-backup:
	sudo tar -xvf traefik-config-backup.tar.gz

echo:
	@echo $(args)

echo-service:
	@echo $(args_service) $(SERVICE_FILE)

env:
	env | sort
