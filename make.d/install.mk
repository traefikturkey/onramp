#########################################################
##
## install commands
##
#########################################################
ACME_JSON_FILE := ./etc/traefik/letsencrypt/acme.json
ACME_JSON_PERMS := 600
export DEBIAN_FRONTEND = noninteractive


# Silence absent and/or empty Ansible inventory warnings
# https://stackoverflow.com/a/59940796/1973777
export ANSIBLE_LOCALHOST_WARNING = False
export ANSIBLE_INVENTORY_UNPARSED_WARNING = False

ifneq (,$(wildcard $(ACME_JSON_FILE)))
BUILD_DEPENDENCIES += $(filter-out $(BUILD_DEPENDENCIES),fix-acme-json-permissions)
endif

fix-acme-json-permissions:
	@if [ -e $(ACME_JSON_FILE) ]; then \
		if [ $$(stat -c %a $(ACME_JSON_FILE)) != "$(ACME_JSON_PERMS)" ]; then \
			echo "Fixing permissions on $(ACME_JSON_FILE)"; \
			sudo chmod $(ACME_JSON_PERMS) $(ACME_JSON_FILE); \
		fi \
	fi

build: install-dependencies .env $(BUILD_DEPENDENCIES)
#@echo "build steps completed"

install: build install-docker

.env:
	cp --no-clobber .templates/env.template .env
	$(EDITOR) .env

REPOS = ansible/ansible
MISSING_REPOS := $(foreach repo,$(REPOS),$(if $(shell apt-cache policy | grep $(repo)),,addrepo/$(repo))) 

# If it's not empty, add a value to it
ifneq ($(strip $(MISSING_REPOS)),)
		MISSING_REPOS += update-distro
endif

EXECUTABLES = git nano jq python3-pip yamllint python3-pathspec ansible 
MISSING_PACKAGES := $(foreach exec,$(EXECUTABLES),$(if $(shell dpkg -s "$(exec)" &> /dev/null),,addpackage-$(exec)))

# duck you debian
addrepo/%:
	@if [ "$(shell lsb_release -si | tail -n 1)" = "Ubuntu" ]; then \
		sudo apt-add-repository ppa:$* -y; \
	fi

addpackage-%:
	sudo apt install $* -y 

update-distro:
	sudo apt update
	sudo apt full-upgrade -y
	sudo apt autoremove -y

install-dependencies: .gitconfig $(MISSING_REPOS) $(MISSING_PACKAGES) 

.gitconfig:
	git config -f .gitconfig core.hooksPath .githooks
	git config --local include.path $(shell pwd)/.gitconfig

install-ansible: install-dependencies
	@echo "Installing ansible roles requirements..."
	ansible-playbook ansible/ansible-requirements.yml

nuke-snaps: 
	@echo "Remove the evil that is snaps..."
	ansible-playbook ansible/nuke-snaps.yml

install-docker: install-ansible
	ansible-playbook ansible/install-docker.yml

update-hosts:
	ansible-playbook ansible/update-hosts.yml

install-node-exporter: install-ansible
	ansible-playbook ansible/install-node-exporter.yml

install-nvidia-drivers: install-ansible
	ansible-playbook ansible/install-nvidia-drivers.yml

# kill all vscode instances running on the server
make kill-code:
	ps aux | grep .vscode-server | awk '{print $$2}' | xargs kill

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

#########################################################
##
## make it-mikes-way
##
#########################################################

MIKES_SERVICES := autoheal watchtower joyride dozzle monocker

.PHONY: it-mikes-way mikesway-%
it-mikes-way: start $(addprefix mikesway-,$(MIKES_SERVICES))

mikesway-%:
		make enable-service $*
		make start-service $*

#$(info "install.mk loaded")
