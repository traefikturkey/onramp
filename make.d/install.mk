#########################################################
#
# install commands
#
#########################################################

build: install-dependencies .env $(BUILD_DEPENDENCIES)

install: build install-docker

.env:
	cp .templates/env.template .env
	$(EDITOR) .env

required-dependencies = git nano jq yq yamllint

install-dependencies:
	git config --local include.path $(shell pwd)/.gitconfig
ifneq (0,$(shell which $(required-dependencies) | echo $$?))
	sudo apt-add-repository ppa:rmescandon/yq -y
	sudo apt update
	DEBIAN_FRONTEND=noninteractive sudo apt install $(required-dependencies) -y
endif

install-ansible:
	sudo apt-add-repository ppa:ansible/ansible -y
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