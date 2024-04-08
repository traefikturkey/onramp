#!/bin/bash

###############################################
# AUTHELIA build up script
###############################################

# Include in this script any commands related to the build up of this service.

	envsubst '$${HOST_DOMAIN}' < ./services-scaffold/authelia/authelia-configuration.template > ./etc/authelia/configuration.yml