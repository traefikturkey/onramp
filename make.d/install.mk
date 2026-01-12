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

# Check if Docker is available (used by targets that need Sietch)
DOCKER_AVAILABLE := $(shell command -v docker >/dev/null 2>&1 && docker ps >/dev/null 2>&1 && echo yes || echo no)

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

check-docker:
	@if [ "$(DOCKER_AVAILABLE)" != "yes" ]; then \
		echo ""; \
		echo "ERROR: Docker is not available."; \
		echo ""; \
		echo "Run 'make install' to bootstrap the system and install Docker,"; \
		echo "or run './bootstrap.sh' directly."; \
		echo ""; \
		exit 1; \
	fi

fix-traefik-network:
	@# Fix traefik network if it exists but wasn't created by compose
	@if docker network inspect traefik >/dev/null 2>&1; then \
		LABEL=$$(docker network inspect traefik --format '{{index .Labels "com.docker.compose.network"}}' 2>/dev/null || echo ""); \
		if [ "$$LABEL" != "traefik" ]; then \
			echo "Fixing traefik network (incorrect compose labels)..."; \
			CONTAINERS=$$(docker network inspect traefik --format '{{range .Containers}}{{.Name}} {{end}}' 2>/dev/null || echo ""); \
			if [ -n "$$CONTAINERS" ]; then \
				echo "Disconnecting containers: $$CONTAINERS"; \
				for c in $$CONTAINERS; do \
					docker network disconnect -f traefik "$$c" 2>/dev/null || true; \
				done; \
			fi; \
			docker network rm traefik 2>/dev/null || true; \
			echo "Traefik network removed. Docker Compose will recreate it."; \
		fi; \
	fi

build: install-dependencies check-docker fix-traefik-network ensure-env ensure-external-middleware migrate-legacy-env $(BUILD_DEPENDENCIES)
#@echo "build steps completed"

# Install target: auto-bootstraps if Docker isn't available
install: ## Install OnRamp (bootstraps fresh systems automatically)
ifeq ($(DOCKER_AVAILABLE),yes)
	$(MAKE) build
else
	@echo "Docker not found - running bootstrap..."
	@./bootstrap.sh
	@# After bootstrap, check if docker is now accessible
	@if command -v docker >/dev/null 2>&1 && docker ps >/dev/null 2>&1; then \
		echo "Docker is now available, continuing with build..."; \
		$(MAKE) build; \
	else \
		echo ""; \
		echo "Bootstrap complete. Run 'make continue-install' after refreshing your shell."; \
	fi
endif

# Continue install after shell refresh (post-bootstrap)
continue-install: ## Continue installation after Docker group refresh
ifeq ($(DOCKER_AVAILABLE),yes)
	$(MAKE) build
else
	@echo ""
	@echo "ERROR: Docker is still not accessible."
	@echo ""
	@echo "Your shell session may not have refreshed properly."
	@echo "Try one of the following:"
	@if [ -n "$${VSCODE_IPC_HOOK_CLI:-}" ] || [ -n "$${VSCODE_GIT_ASKPASS_NODE:-}" ]; then \
		echo "  1. Run: make kill-code"; \
		echo "  2. Reconnect to this machine in VSCode"; \
		echo "  3. Run: make continue-install"; \
	else \
		echo "  1. Run: newgrp docker"; \
		echo "  2. Or log out and log back in"; \
		echo "  3. Then run: make continue-install"; \
	fi
	@echo ""
	@exit 1
endif

# Ensure environment is configured (new modular system or legacy)
ensure-env: services-enabled/.env ensure-env-files
	@true

# Ensure external-enabled has the default traefik middleware
# Services reference default-headers@file which requires this file
ensure-external-middleware: external-enabled/middleware.yml
	@true

external-enabled/middleware.yml:
	@mkdir -p external-enabled
	@cp external-available/middleware.yml external-enabled/middleware.yml
	@echo "Initialized external-enabled/middleware.yml"

# Create services-enabled/.env from template if needed
# Handles three migration paths:
# 1. Legacy master: .env exists -> migrated during build
# 2. Feature branch: environments-enabled/ OR environments-available/ exists -> migrated during build
# 3. Fresh install: scaffold from template (wizard runs via ensure-env-files)
services-enabled/.env:
	@mkdir -p services-enabled
	@if [ -f .env ]; then \
		echo "Legacy .env found - will be migrated during build"; \
	elif [ -d environments-enabled ] || [ -d environments-available ]; then \
		echo "Feature branch detected - will be migrated during build"; \
	elif [ -f services-scaffold/onramp/.env.template ]; then \
		echo "Creating initial environment configuration..."; \
		$(MAKE) scaffold-build onramp || cp services-scaffold/onramp/.env.template services-enabled/.env; \
	else \
		echo "No environment template found. Creating minimal .env..."; \
		touch services-enabled/.env; \
	fi


REPOS = ansible/ansible
MISSING_REPOS := $(foreach repo,$(REPOS),$(if $(shell apt-cache policy | grep $(repo)),,addrepo/$(repo))) 

# If it's not empty, add a value to it
ifneq ($(strip $(MISSING_REPOS)),)
		MISSING_REPOS += update-distro
endif

EXECUTABLES = git nano jq python3-pip yamllint python3-pathspec ansible
MISSING_PACKAGES := $(foreach exec,$(EXECUTABLES),$(if $(shell dpkg -s "$(exec)" >/dev/null 2>&1),,addpackage-$(exec)))

# Add PPA repository (Ubuntu only, uses /etc/os-release instead of lsb_release)
addrepo/%:
	@if [ -f /etc/os-release ] && grep -q '^ID=ubuntu' /etc/os-release; then \
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

# Kill all vscode-server instances on the host
kill-code:
	ps aux | grep .vscode-server | awk '{print $$2}' | xargs kill

#########################################################
##
## staging commands
##
#########################################################

start-staging: build ## start the staging and wait for the acme staging certs to be issued
	export ACME_CASERVER=https://acme-staging-v02.api.letsencrypt.org/directory && $(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) up -d --force-recreate --pull=missing
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
## Validation Checks
##
#########################################################

check-yaml: install-dependencies ## Check YAML files
	yamllint -c .yamllint .

check-cf:
	@if [ "$(CF_API_EMAIL)" != "" ]; then echo "CF_API_EMAIL : PASSED"; else echo "FAILED : Please set your CF_API_EMAIL in the .env file"; fi
	@if [ "$(CF_DNS_API_TOKEN)" != "" ]; then echo "CF_DNS_API_TOKEN : PASSED"; else echo "FAILED : Please set your CF_DNS_API_TOKEN in the .env file"; fi
	@if [ "$(HOST_NAME)" != "" ]; then echo "HOST_NAME: PASSED"; else echo "FAILED : Please set your HOST_NAME in the .env file"; fi
	@if [ "$(HOST_DOMAIN)" != "" ]; then echo "HOST_DOMAIN : PASSED"; else echo "FAILED : Please set your HOST_DOMAIN in the .env file"; fi

check-authentik:
	@if [ "$(AUTHENTIK_SECRET_KEY)" != "" ]; then echo "AUTHENTIK_SECRET_KEY : PASSED"; else echo "FAILED : Please set your AUTHENTIK_SECRET_KEY in the .env file"; fi
	@if [ "$(PG_PASS_AUTHENTIK)" != "" ]; then echo "PG_PASS_AUTHENTIK : PASSED"; else echo "FAILED : Please set your PG_PASS_AUTHENTIK in the .env file"; fi
	@if [ "$(AUTHENTIK_BOOTSTRAP_PASSWORD)" != "" ]; then echo "AUTHENTIK_BOOTSTRAP_PASSWORD: PASSED"; else echo "FAILED : Please set your AUTHENTIK_BOOTSTRAP_PASSWORD in the .env file"; fi

check-authelia:
	@if [ "$(AUTHELIA_JWT_SECRET)" != "" ]; then echo "AUTHELIA_JWT_SECRET : PASSED"; else echo "FAILED : Please set your AUTHELIA_JWT_SECRET in the .env file"; fi
