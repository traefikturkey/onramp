#########################################################
##
## helper commands
##
#########################################################

bash-run:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) run -it --rm $(SERVICE_PASSED_DNCASED) sh

bash-exec:
	$(DOCKER_COMPOSE) $(DOCKER_COMPOSE_FLAGS) exec $(SERVICE_PASSED_DNCASED) sh

edit-env: ## edit the .env file using the editor specified in the EDITOR variable
	$(EDITOR) .env

generate-matrix-config:
	$(DOCKER_COMMAND) run -it --rm  -v ./etc/synapse:/data  -e SYNAPSE_SERVER_NAME=synapse.traefikturkey.icu -e SYNAPSE_REPORT_STATS=yes matrixdotorg/synapse:latest generate	

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

excuse: ## get programming excuse
	@curl -s programmingexcuses.com | egrep -o "<a[^<>]+>[^<>]+</a>" | egrep -o "[^<>]+" | sed -n 2p

test-smtp: ## test smtp
	envsubst .templates/smtp.template | nc localhost 25

# https://stackoverflow.com/questions/7117978/gnu-make-list-the-values-of-all-variables-or-macros-in-a-particular-run
echo:
	@$(MAKE) -pn | grep -A1 "^# makefile"| grep -v "^#\|^--" | grep -e "^[A-Z]+*" | sort

env: ## show environment variables sorted
	@env | sort