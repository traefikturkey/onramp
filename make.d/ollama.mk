
ifndef OLLAMA_CONTAINER_NAME
OLLAMA_CONTAINER_NAME=ollama
endif

ollama_cmd = @docker exec -it $(OLLAMA_CONTAINER_NAME) $(OLLAMA_CONTAINER_NAME)

pull-model: ## pull a ollama model with the name of the first argument passed 
	$(ollama_cmd) pull $(first_arg)


update-ollama-models:
	$(shell pwd)/make.d/scripts/update-ollama-models.sh --docker