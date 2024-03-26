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

ifneq ("$(wildcard $(ACME_JSON_FILE))","")
  BUILD_DEPENDENCIES += fix-acme-json-permissions
endif

fix-acme-json-permissions:
	@if [ -e $(ACME_JSON_FILE) ]; then \
		if [ $$(stat -c %a $(ACME_JSON_FILE)) != "$(ACME_JSON_PERMS)" ]; then \
			echo "Fixing permissions on $(ACME_JSON_FILE)"; \
			sudo chmod $(ACME_JSON_PERMS) $(ACME_JSON_FILE); \
		fi \
	fi

build: install-dependencies .env $(BUILD_DEPENDENCIES)

install: build install-docker

.env:
	cp --no-clobber .templates/env.template .env
	$(EDITOR) .env

REPOS = rmescandon/yq ansible/ansible
MISSING_REPOS := $(foreach repo,$(REPOS),$(if $(shell apt-cache policy | grep $(repo)),,addrepo/$(repo))) 

# If it's not empty, add a value to it
ifneq ($(strip $(MISSING_REPOS)),)
    MISSING_REPOS += update-distro
endif

EXECUTABLES = git nano jq yq python3-pip yamllint python3-pathspec ansible 
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

install-docker: install-ansible
	ansible-playbook ansible/install-docker.yml

update-hosts:
	ansible-playbook ansible/update-hosts.yml

install-node-exporter: install-ansible
	ansible-playbook ansible/install-node-exporter.yml

install-nvidia-drivers: install-ansible
	ansible-playbook ansible/install-nvidia-drivers.yml
