# include .env variable in the current environment
ifneq (,$(wildcard ./.env))
    include .env
    export
endif

# any disabled-*.yml docker-compose files will be ignored
disabled_files := $(wildcard disabled-*.yml)
# all other *.yml files in the current directory will be included 
# when running make commands that call docker compose
compose_files := $(filter-out $(disabled_files), $(wildcard *.yml))
args := $(foreach file, $(compose_files), -f $(file))

# get the boxes ip address and the current users id and group id
export HOSTIP := $(shell ip route get 1.1.1.1 | grep -oP 'src \K\S+')
export PUID 	:= $(shell id -u)
export PGID 	:= $(shell id -g)

# check if we should use docker-compose or docker compose
ifeq (, $(shell which docker-compose))
	DOCKER_COMPOSE := docker compose
else
	DOCKER_COMPOSE := docker-compose
endif

# use letsencrypt staging url if we run commands like:
# make up staging
ifeq (staging, $(word 2,$(MAKECMDGOALS)))
	export ACME_CASERVER := https://acme-staging-v02.api.letsencrypt.org/directory
endif

# this is the default target run if no other targets are passed to make
# i.e. if you just type: make
start: 
	$(DOCKER_COMPOSE) $(args) up -d --force-recreate

up: 
	$(DOCKER_COMPOSE)$(args) up

down: 
	$(DOCKER_COMPOSE) $(args) down

echo:
	@echo $(args)

pull:
	$(DOCKER_COMPOSE) $(args) pull

logs:
	$(DOCKER_COMPOSE)  $(args) logs -f

restart: down start

update: down pull start

clear-certs:
	rm etc/letsencrypt/acme.json

env:
	env | sort