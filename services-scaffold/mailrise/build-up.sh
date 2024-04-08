#!/bin/bash

###############################################
# MAILRISE build up script
###############################################

# Include in this script any commands related to the build up of this service.

envsubst '$${MAILRISE_EMAIL}, $${MAILRISE_WEBHOOK}' < ./services-scaffold/mailrise/mailrise.template > ./etc/mailrise/mailrise.conf