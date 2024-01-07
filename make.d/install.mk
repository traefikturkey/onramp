#########################################################
#
# install commands
#
#########################################################
distro := $(shell lsb_release -is)


check-distro:
	@echo $(distro)


ifeq ($(distro),Ubuntu)
    ANSIBLE_APT_ADD_REPO := sudo apt-add-repository ppa:ansible/ansible -y
    YQ_APT_ADD_REPO 	 := sudo apt-add-repository ppa:rmescandon/yq -y
else
    YQ_APT_ADD_REPO      :=
    ANSIBLE_APT_ADD_REPO :=
endif

build: install-dependencies .env $(BUILD_DEPENDENCIES)

install: build install-docker

.env:
	cp .templates/env.template .env
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

install-node-exporter: install-ansible
	ansible-playbook ansible/install-node-exporter.yml

install-nvidia-drivers: install-ansible
	ansible-playbook ansible/install-nvidia-drivers.yml
