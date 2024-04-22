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

# this is the default target run if no other targets are passed to make
# i.e. if you just type: make

#########################################################
##
## basic commands
##
#########################################################

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

bash-run:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) run -it --rm $(SERVICE_PASSED_DNCASED) sh

bash-exec:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) exec $(SERVICE_PASSED_DNCASED) sh

include make.d/install.mk

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
enable-service: etc/$(SERVICE_PASSED_DNCASED) services-enabled/$(SERVICE_PASSED_DNCASED).yml ## Enable a service by creating a symlink to the service file in the services-enabled folder

etc/$(SERVICE_PASSED_DNCASED):
	@mkdir -p ./etc/$(SERVICE_PASSED_DNCASED)

services-enabled/$(SERVICE_PASSED_DNCASED).yml:
ifneq (,$(wildcard ./services-available/$(SERVICE_PASSED_DNCASED).yml))
	@echo "Enabling $(SERVICE_PASSED_DNCASED)..."
	@ln -s ../services-available/$(SERVICE_PASSED_DNCASED).yml ./services-enabled/$(SERVICE_PASSED_DNCASED).yml || true
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

start-dev: COMPOSE_IGNORE_ORPHANS = true 
start-dev: build services-dev
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_DEVELOPMENT_FLAGS) up -d --force-recreate $(SERVICE_PASSED_DNCASED)

stop-dev:
	-$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_DEVELOPMENT_FLAGS) stop $(SERVICE_PASSED_DNCASED)

services-dev:
	mkdir -p ./services-dev

#########################################################
##
## compose commands
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
## staging commands
##
#########################################################

start-staging: build ## start the staging and wait for the acme staging certs to be issued
	ACME_CASERVER=https://acme-staging-v02.api.letsencrypt.org/directory $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --force-recreate
	@echo "waiting $(CF_RESOLVER_WAITTIME) seconds for cert DNS propogation..."
	@sleep $(CF_RESOLVER_WAITTIME)
	@echo "open https://$(HOST_NAME).$(HOST_DOMAIN)/traefik in a browser"
	@echo "and check that you have a staging cert from LetsEncrypt!"
	@echo ""
	@echo "if you don't get a LetsEncrypt staging cert run the following command and look for error messages:"
	@echo "docker compose logs | grep acme"
	@echo ""
	@echo "otherwise run the following command if you successfully got a staging certificate:"
	@echo "make down-staging"

down-staging: ## stop the staging and delete the acme staging certs
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) down
	$(MAKE) clean-acme

#########################################################
##
## list commands
##
#########################################################

list-games: ## list available games
	@ls -1 ./services-available/games | sed -n 's/\.yml$ //p'

list-services: ## list available services
	@ls -1 ./services-available/ | sed -e 's/\.yml$ //'

list-overrides: ## list available overrides
	@ls -1 ./overrides-available/ | sed -e 's/\.yml$ //'

list-external: ## list available external services
	@ls -1 ./etc/traefik/available/ | sed -e 's/\.yml$ //'

list-enabled: ## list enabled services
	@printf "%s\n" $(shell ls -1 ./services-enabled/ | sed -e 's/\.yml$ //' )

print-enabled: ## print enabled services
	@printf "%s\n" "Here are your enabled services : " $(shell ls -1 ./services-enabled/ | sed -e 's/\.yml$ //' )

count-enabled: ## count enabled services
	@echo "Total services run in onramp (this is excluding Traefik, and multi-services composes are counted as one) : " $(shell make list-enabled | wc -l )

list-count: print-enabled count-enabled ## list enabled services and count them


#########################################################
##
## build related commands
##
#########################################################

ifneq (,$(wildcard ./services-enabled/authelia.yml))
	BUILD_DEPENDENCIES += etc/authelia/configuration.yml
endif

etc/authelia/configuration.yml:
	envsubst '$${HOST_DOMAIN}' < ./etc/authelia/configuration.template > ./etc/authelia/configuration.yml

ifneq (,$(wildcard ./services-enabled/adguard.yml))
	BUILD_DEPENDENCIES += etc/adguard/conf/AdGuardHome.yaml
endif

etc/adguard/conf/AdGuardHome.yaml:
	envsubst '$${ADGUARD_PASSWORD}, $${ADGUARD_USER}, $${HOST_DOMAIN}' < ./etc/adguard/conf/AdGuardHome.template > ./etc/adguard/conf/AdGuardHome.yaml

ifneq (,$(wildcard ./services-enabled/pihole.yml))
	BUILD_DEPENDENCIES += etc/pihole/dnsmasq/03-custom-dns-names.conf
endif

etc/pihole/dnsmasq/03-custom-dns-names.conf:
	envsubst '$${HOST_DOMAIN}, $${HOSTIP} ' < ./etc/pihole/dns.template > ./etc/pihole/dnsmasq/03-custom-dns-names.conf

ifneq (,$(wildcard ./services-enabled/dashy.yml))
	BUILD_DEPENDENCIES += etc/dashy/dashy-config.yml
endif

etc/dashy/dashy-config.yml:
	mkdir -p ./etc/dashy
	touch ./etc/dashy/dashy-config.yml

ifneq (,$(wildcard ./services-enabled/prometheus.yml))
	BUILD_DEPENDENCIES += etc/prometheus/conf
endif

etc/prometheus/conf:
	mkdir -p etc/prometheus/conf
	cp --no-clobber --recursive	etc/prometheus/conf-originals/* etc/prometheus/conf


ifneq (,$(wildcard ./services-enabled/recyclarr.yml))
	BUILD_DEPENDENCIES += etc/recyclarr/recyclarr.yml
endif

etc/recyclarr/recyclarr.yml:
	cp --no-clobber .templates/recyclarr.template .etc/recyclarr/recyclarr.yml


ifneq (,$(wildcard ./services-enabled/gatus.yml))
	BUILD_DEPENDENCIES += etc/gatus/config.yaml
endif

etc/gatus/config.yaml:
	cp --no-clobber .templates/gatus.template .etc/gatus/config.yaml

#########################################################
##
## override commands
##
#########################################################

enable-override: overrides-enabled/$(SERVICE_PASSED_DNCASED).yml
overrides-enabled/$(SERVICE_PASSED_DNCASED).yml:
	@ln -s ../overrides-available/$(SERVICE_PASSED_DNCASED).yml ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml || true

remove-override: disable-override ## disble the override before removing it
disable-override:
	rm ./overrides-enabled/$(SERVICE_PASSED_DNCASED).yml 

#########################################################
##
## external commands
##
#########################################################

disable-external: ## disable an external service
	rm ./etc/traefik/enabled/$(SERVICE_PASSED_DNCASED).yml

enable-external: ## enable an external service
	@cp  --no-clobber ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml ./etc/traefik/enabled/$(SERVICE_PASSED_DNCASED).yml || true

create-external: ## create an external service
	envsubst '$${SERVICE_PASSED_DNCASED},$${SERVICE_PASSED_UPCASED}' < ./.templates/external.template > ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml
	$(EDITOR) ./etc/traefik/available/$(SERVICE_PASSED_DNCASED).yml

#########################################################
##
## helper commands
##
#########################################################

edit-env: ## edit the .env file using the editor specified in the EDITOR variable
	$(EDITOR) .env

generate-matrix-config:
	docker run -it --rm  -v ./etc/synapse:/data  -e SYNAPSE_SERVER_NAME=synapse.traefikturkey.icu -e SYNAPSE_REPORT_STATS=yes matrixdotorg/synapse:latest generate	

#########################################################
##
## arrs api-key retrieval
##
#########################################################

retrieve-apikey: ## retrieve api key from arrs
	@grep -oP '(?<=ApiKey>).*?(?=</ApiKey>)' ./etc/$${SERVICE_PASSED_DNCASED}/config.xml

# include additional make commands
include make.d/backup.mk

include make.d/cleanup.mk

include make.d/database.mk

include make.d/prestashop.mk

include make.d/testing.mk

include make.d/checks.mk

include make.d/help.mk

include make.d/ai.mk

include make.d/ollama.mk