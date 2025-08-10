#!/bin/bash

###############################################
# KANEO build up script
###############################################

# Include in this script any commands related to the build up of this service.

mkdir -p ./etc/kaneo/db
chown -R $USER:$USER ./etc/kaneo
chmod g+s ./etc/kaneo