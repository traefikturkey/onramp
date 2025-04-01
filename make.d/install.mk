#########################################################
##
## install commands
##
#########################################################

# Silence absent and/or empty Ansible inventory warnings
# https://stackoverflow.com/a/59940796/1973777
export ANSIBLE_LOCALHOST_WARNING = False
export ANSIBLE_INVENTORY_UNPARSED_WARNING = False

REPOS = ansible/ansible
MISSING_REPOS := $(foreach repo,$(REPOS),$(if $(shell apt-cache policy | grep $(repo)),,addrepo/$(repo))) 

# If it's not empty, add a value to it
ifneq ($(strip $(MISSING_REPOS)),)
	MISSING_REPOS += update-distro
endif

EXECUTABLES = git nano jq python3-pip yamllint python3-pathspec ansible 
MISSING_PACKAGES := $(foreach exec,$(EXECUTABLES),$(if $(shell dpkg -s "$(exec)" &> /dev/null),,addpackage-$(exec)))

# Check for podman command
ifneq ($(shell command -v podman >/dev/null 2>&1 && echo found),found)
    # If podman is not found, check for docker command
    ifneq ($(shell command -v docker >/dev/null 2>&1 && echo found),found)
        # If neither podman nor docker is found, add install-docker to BUILD_DEPENDENCIES
        BUILD_DEPENDENCIES += install-docker
    endif
endif

# duck you debian
addrepo/%:
	@if [ "$(shell lsb_release -si | tail -n 1)" = "Ubuntu" ]; then \
		sudo apt-add-repository ppa:$* -y; \
	fi

addpackage-%:
	sudo apt install $* -y 

export DEBIAN_FRONTEND = noninteractive

update-distro:
	sudo apt update
	sudo apt full-upgrade -y
	sudo apt autoremove -y

install: update-distro build 

build: .env .gitconfig $(BUILD_DEPENDENCIES) $(MISSING_REPOS) $(MISSING_PACKAGES) 

.env:
	cp --no-clobber .templates/env.template .env
	$(EDITOR) .env

.gitconfig:
	git config -f .gitconfig core.hooksPath .githooks
	git config --local include.path $(shell pwd)/.gitconfig

install-ansible-requirements: 
	@echo "Installing ansible roles requirements..."
	ansible-playbook ansible/ansible-requirements.yml

nuke-snaps: 
	@echo "Remove the evil that is snaps..."
	ansible-playbook ansible/nuke-snaps.yml

install-docker: install-ansible-requirements
	ansible-playbook ansible/install-docker.yml

install-node-exporter: install-ansible-requirements
	ansible-playbook ansible/install-node-exporter.yml

install-nvidia-drivers: install-ansible-requirements
	ansible-playbook ansible/install-nvidia-drivers.yml

update-hosts:
	ansible-playbook ansible/update-hosts.yml

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
