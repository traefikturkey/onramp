#!/bin/bash

###############################################
# RECYCLARR build up script
###############################################

# Include in this script any commands related to the build up of this service.

mkdir -p ./etc/recyclarr/repo

cp --no-clobber ./services-scaffold/recyclarr/recyclarr.template ./etc/recyclarr/recyclarr.yml