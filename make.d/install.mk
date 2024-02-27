#########################################################
##
## install commands
##
#########################################################
distro := $(shell lsb_release -is)


check-distro: ## check distro
	@echo $(distro)


ifeq ($(distro),Ubuntu)
    ANSIBLE_APT_ADD_REPO := sudo apt-add-repository ppa:ansible/ansible -y
    YQ_APT_ADD_REPO 	 := sudo apt-add-repository ppa:rmescandon/yq -y
else
    YQ_APT_ADD_REPO      :=
    ANSIBLE_APT_ADD_REPO :=
endif

ACME_JSON_FILE := ./etc/traefik/letsencrypt/acme.json
ACME_JSON_PERMS := 600

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

EXECUTABLES = git nano jq yq pip yamllint
MISSING_PACKAGES := $(foreach exec,$(EXECUTABLES),$(if $(shell which $(exec)),,addpackage-$(exec)))

addrepositories:
	$(YQ_APT_ADD_REPO)
	sudo apt update

addpackage-%: addrepositories
	DEBIAN_FRONTEND=noninteractive sudo apt install $* -y

install-dependencies: .gitconfig $(MISSING_PACKAGES)

.gitconfig:
	git config -f .gitconfig core.hooksPath .githooks
	git config --local include.path $(shell pwd)/.gitconfig

install-ansible:
	#sudo apt-add-repository ppa:ansible/ansible -y
	$(APT_ADD_REPO)	
	sudo apt update
	sudo apt install ansible -y
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
