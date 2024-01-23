#########################################################
##
## help commands
##
#########################################################


# help:  ## show this help text
# 	@awk -vG=$$(tput setaf 2) -vR=$$(tput sgr0) ' \
# 	  match($$0, "^(([^#:]*[^ :]) *:)?([^#]*)##([^#].+|)$$",a) { \
# 	    if (a[2] != "") { printf "    make %s%-18s%s %s\n", G, a[2], R, a[4]; next }\
# 	    if (a[3] == "") { print a[4]; next }\
# 	    printf "\n%-36s %s\n","",a[4]\
# 	  }' Makefile

#Extract the help command logic into a function
define help_function
	@awk -vG=$$(tput setaf 2) -vR=$$(tput sgr0) ' \
		match($$0, "^(([^#:]*[^ :]) *:)?([^#]*)##([^#].+|)$$",a) { \
		if (a[2] != "") { printf "    make %s%-18s%s %s\n", G, a[2], R, a[4]; next }\
		if (a[3] == "") { print a[4]; next }\
		printf "\n%-36s %s\n","",a[4]\
		}' $(1)
endef

# # Define the help target and call the help function
help:
	$(call help_function, Makefile)


# .DEFAULT_GOAL := help

# Stolen from here 
# https://gist.github.com/prwhite/8168133
