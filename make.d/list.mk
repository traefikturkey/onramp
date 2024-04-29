#########################################################
##
## list commands
##
#########################################################

list-games: ## list available games
	@ls -1 ./services-available/games | sed -n 's/\.yml$ //p'

list-services: ## list available services
	@ls -1 ./services-available/ | sed -e 's/\.yml$ //'

list-overrides: ## list available overrides
	@ls -1 ./overrides-available/ | sed -e 's/\.yml$ //'

list-external: ## list available external services
	@ls -1 ./etc/traefik/available/ | sed -e 's/\.yml$ //'

list-enabled: ## list enabled services
	@printf "%s\n" $(shell ls -1 ./services-enabled/ | sed -e 's/\.yml$ //' )

print-enabled: ## print enabled services
	@printf "%s\n" "Here are your enabled services : " $(shell ls -1 ./services-enabled/ | sed -e 's/\.yml$ //' )

count-enabled: ## count enabled services
	@echo "Total services run in onramp (this is excluding Traefik, and multi-services composes are counted as one) : " $(shell make list-enabled | wc -l )

list-count: print-enabled count-enabled ## list enabled services and count them