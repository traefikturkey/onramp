#!/bin/bash

###############################################
# ADGUARD build up script
###############################################

# Include in this script any commands related to the build up of this service.

mkdir -p ./etc/adguard/conf
mkdir -p ./etc/adguard/work

envsubst '$${ADGUARD_PASSWORD}, $${ADGUARD_USER}, $${HOST_DOMAIN}' < ./services-scaffold/adguard/AdGuardHome.template > ./etc/adguard/conf/AdGuardHome.yaml