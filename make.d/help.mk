#########################################################
##
## Help Commands
##
#########################################################

# Parses ## comments after targets to generate help text
# Source: https://gist.github.com/prwhite/8168133
define help_function
	@awk -vG=$$(tput setaf 2) -vR=$$(tput sgr0) ' \
		match($$0, "^(([^#:]*[^ :]) *:)?([^#]*)##([^#].+|)$$",a) { \
		if (a[2] != "") { printf "    make %s%-18s%s %s\n", G, a[2], R, a[4]; next }\
		if (a[3] == "") { print a[4]; next }\
		printf "\n%-36s %s\n","",a[4]\
		}' $(1)
endef

help: ## Show available targets
	$(call help_function, Makefile)
