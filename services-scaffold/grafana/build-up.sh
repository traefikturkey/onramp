#!/bin/bash

###############################################
# GRAFANA build up script
###############################################

# Include in this script any commands related to the build up of this service.

mkdir -p ./etc/grafana/provisioning/alerting
mkdir -p ./etc/grafana/provisioning/dashboards
mkdir -p ./etc/grafana/provisioning/datasources
mkdir -p ./etc/grafana/provisioning/notifiers
mkdir -p ./etc/grafana/provisioning/plugins

cp --no-clobber ./services-scaffold/grafana/loki.yml ./etc/grafana/provisioning/datasources/loki.yml
cp --no-clobber ./services-scaffold/grafana/prometheus.yml ./etc/grafana/provisioning/datasources/prometheus.yml
cp --no-clobber ./services-scaffold/grafana/alertmanager.yml ./etc/grafana/provisioning/plugins/alertmanager.yml