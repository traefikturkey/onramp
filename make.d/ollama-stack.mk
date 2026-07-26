#########################################################
##
## Ollama Capability Stack
##
#########################################################

OLLAMA_STACK_SERVICES := ollama ollama-webui docling searxng pipelines
OLLAMA_STACK_COMPOSE_FILES := $(foreach service,$(OLLAMA_STACK_SERVICES),$(wildcard services-enabled/$(service).yml))
OLLAMA_STACK_OVERRIDE_FILES := $(foreach service,$(OLLAMA_STACK_SERVICES),$(wildcard overrides-enabled/$(service)-*.yml))
OLLAMA_STACK_FLAGS := $(ENV_FLAGS) --project-directory ./ -f docker-compose.yml $(foreach file,$(OLLAMA_STACK_COMPOSE_FILES) $(OLLAMA_STACK_OVERRIDE_FILES),-f $(file))

.PHONY: enable-ollama-stack check-ollama-stack-enabled plan-ollama-stack deploy-ollama-stack validate-ollama-stack

enable-ollama-stack: ## Enable Ollama, Open WebUI, Docling, SearXNG, and Pipelines
	@set -e; \
	for service in $(OLLAMA_STACK_SERVICES); do \
		$(MAKE) enable-service $$service; \
	done

check-ollama-stack-enabled:
	@missing=""; \
	for service in $(OLLAMA_STACK_SERVICES); do \
		if [ ! -e services-enabled/$$service.yml ]; then \
			missing="$$missing $$service"; \
		fi; \
	done; \
	if [ -n "$$missing" ]; then \
		echo "Missing enabled Ollama stack services:$$missing"; \
		echo "Run: make enable-ollama-stack"; \
		exit 2; \
	fi

plan-ollama-stack: check-ollama-stack-enabled ## Validate and preview changes to the Ollama stack
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) config --quiet
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) --dry-run up -d

deploy-ollama-stack: check-ollama-stack-enabled ## Deploy the Ollama stack after reviewing plan-ollama-stack
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) config --quiet
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) up -d

validate-ollama-stack: check-ollama-stack-enabled ## Validate Ollama stack DNS and HTTP reachability from Open WebUI
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) exec -T ollama-webui getent hosts ollama docling-serve searxng pipelines
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) exec -T ollama-webui python -c 'import urllib.request; urllib.request.urlopen("http://ollama:11434/api/tags", timeout=20)'
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) exec -T ollama-webui python -c 'import urllib.request; urllib.request.urlopen("http://searxng:8080/search?q=test&format=json", timeout=20)'
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) exec -T ollama-webui python -c 'import urllib.request; urllib.request.urlopen("http://pipelines:9099/", timeout=20)'
	$(DOCKER_COMPOSE) $(OLLAMA_STACK_FLAGS) exec -T ollama-webui python -c 'import urllib.request; urllib.request.urlopen("http://docling-serve:5001/openapi.json", timeout=20)'
