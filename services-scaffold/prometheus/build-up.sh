#!/bin/bash

###############################################
# PROMETHEUS build up script
###############################################

# Include in this script any commands related to the build up of this service.

mkdir -p ./etc/prometheus/conf/alert-rules-available
mkdir -p ./etc/prometheus/conf/alert-rules-enabled
mkdir -p ./etc/prometheus/conf/blackbox
mkdir -p ./etc/prometheus/conf/nodes
mkdir -p ./etc/prometheus/conf/plugins

cp --no-clobber ./services-scaffold/prometheus/alert-rules.yml ./etc/prometheus/conf/alert-rules-available/alert-rules.yml
cp --no-clobber ./services-scaffold/prometheus/alertmanager.yml ./etc/prometheus/conf/alert-manager.yml
cp --no-clobber ./services-scaffold/prometheus/cameras.json.sample ./etc/prometheus/conf/blackbox/cameras.json.sample
cp --no-clobber ./services-scaffold/prometheus/websites.json.sample ./etc/prometheus/conf/blackbox/websites.json.sample
cp --no-clobber ./services-scaffold/prometheus/blackbox.yml ./etc/prometheus/conf/blackbox.yml
cp --no-clobber ./services-scaffold/prometheus/docker_host.json ./etc/prometheus/conf/nodes/docker_hosts.json
cp --no-clobber ./services-scaffold/prometheus/linux_servers.json.sample ./etc/prometheus/conf/nodes/linux_servers.json.sample
cp --no-clobber ./services-scaffold/prometheus/windows_servers.json.sample ./etc/prometheus/conf/nodes/windows_servers.json.sample
cp --no-clobber ./services-scaffold/prometheus/prometheus.yml ./etc/prometheus/conf/prometheus.yml