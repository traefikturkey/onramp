#########################################################
##
## install commands
##
#########################################################
ACME_JSON_FILE := ./etc/traefik/letsencrypt/acme.json
ACME_JSON_PERMS := 600
export DEBIAN_FRONTEND = noninteractive

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

EXECUTABLES = git nano jq yq python3-pip yamllint python3-pathspec ansible
MISSING_PACKAGES := $(foreach exec,$(EXECUTABLES),$(if $(shell dpkg -s "$(exec)" &> /dev/null),,addpackage-$(exec)))

addrepo/%:
	sudo apt-add-repository ppa:$* -y

addpackage-%: 
	sudo apt install $* -y

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
