#########################################################
##
## helper commands
##
#########################################################

bash-run:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) run -it --rm $(SERVICE_PASSED_DNCASED) sh

bash-exec:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) exec $(SERVICE_PASSED_DNCASED) sh

#########################################################
##
## arrs api-key retrieval
##
#########################################################

retrieve-apikey: ## retrieve api key from arrs
	@grep -oP '(?<=ApiKey>).*?(?=</ApiKey>)' ./etc/$${SERVICE_PASSED_DNCASED}/config.xml


#########################################################
##
## test and debugging commands
##
#########################################################


# https://stackoverflow.com/questions/7117978/gnu-make-list-the-values-of-all-variables-or-macros-in-a-particular-run
echo:
	@$(MAKE) -pn | grep -A1 "^# makefile"| grep -v "^#\|^--" | grep -e "^[A-Z]+*" | sort
