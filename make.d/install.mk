#########################################################
#
# install commands
#
#########################################################

required-dependencies = git nano jq yq

install-dependencies:
echo $(shell which $(required-dependencies) | echo $?)
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