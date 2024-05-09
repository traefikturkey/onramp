#!/bin/bash

SERVICE_NAME=$1

grep -oE "\./etc/$SERVICE_NAME\S*" "services-enabled/$SERVICE_NAME.yml" | sed 's/:.*//' | while read -r volume; do
  if [[ "$volume" == *.* ]]; then
    mkdir -p "$(dirname "$volume")"
    touch "$volume"
  else
    mkdir -p "$volume"
  fi
  sleep 1
done