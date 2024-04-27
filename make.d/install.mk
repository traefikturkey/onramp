#########################################################
##
## install commands
##
#########################################################

ifneq ("$(wildcard $(ACME_JSON_FILE))","")
  BUILD_DEPENDENCIES += fix-acme-json-permissions
endif

fix-acme-json-permissions:
	ACME_JSON_FILE=./etc/traefik/letsencrypt/acme.json
	ACME_JSON_PERMS=600
	@if [ -e ${ACME_JSON_FILE} ]; then \
		if [ $$(stat -c %a ${ACME_JSON_FILE}) != "${ACME_JSON_PERMS}" ]; then \
			echo "Fixing permissions on ${ACME_JSON_FILE}"; \
			sudo chmod ${ACME_JSON_PERMS} ${ACME_JSON_FILE}; \
		fi \
	fi

build: .env $(BUILD_DEPENDENCIES)

install: build 

.env:
	cp --no-clobber .templates/env.template .env
	$(EDITOR) .env

#########################################################
##
## staging commands
##
#########################################################

start-staging: build ## start the staging and wait for the acme staging certs to be issued
	ACME_CASERVER=https://acme-staging-v02.api.letsencrypt.org/directory $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --force-recreate
	@echo "waiting $(CF_RESOLVER_WAITTIME) seconds for cert DNS propogation..."
	@echo ""
	@echo "While you wait you should setup a DNS record pointing $(HOST_NAME).$(HOST_DOMAIN) to $(HOSTIP) for this server!"
	@echo "If you will be using Joyride here are the entries you will need for dnsmasq/pihole:"
	@echo ""
	@echo "address=/$(HOST_NAME).$(HOST_DOMAIN)/$(HOSTIP)"
	@echo "server=/$(HOST_DOMAIN)/$(HOSTIP)#54"
	@echo ""
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

clean-acme: ## remove acme certificate file
	@echo "removing acme certificate file"
	-sudo rm etc/traefik/letsencrypt/acme.json

#########################################################
##
## helper commands
##
#########################################################

# kill all vscode instances running on the server
make kill-code:
	ps aux | grep .vscode-server | awk '{print $2}' | xargs kill