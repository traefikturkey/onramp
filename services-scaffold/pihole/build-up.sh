#!/bin/bash

###############################################
# PIHOLE build up script
###############################################

# Include in this script any commands related to the build up of this service.

mkdir -p ./etc/pihole/dnsmasq

envsubst '$${HOST_DOMAIN}, $${HOSTIP} ' < ./services-scaffold/pihole/dns.template > ./etc/pihole/dnsmasq/03-custom-dns-names.conf