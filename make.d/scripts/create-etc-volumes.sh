#!/bin/bash

SERVICE_NAME=$1

grep -oE "\./etc/$SERVICE_NAME\S*" "services-enabled/$SERVICE_NAME.yml" | sed 's/:.*//' | while read -r volume; do
  if [[ "${volume#.}" == *.* ]]; then
    mkdir -p "$(dirname "$volume")"
    touch "$volume"
  else
    mkdir -p "$volume"
  fi
  sleep 1
done

# Copy config files from the templates directory to the etc directory, primarily used for the *arr services
# Define source and destination directories
SOURCE_DIR="./templates/services/$SERVICE_NAME/"
DEST_DIR="./etc/$SERVICE_NAME/"

# Check if the source directory exists
if [ -d "$SOURCE_DIR" ]; then
    # Ensure destination directory exists
    mkdir -p "$DEST_DIR"
    
    # Use rsync to copy only new files
    rsync -a --ignore-existing "$SOURCE_DIR" "$DEST_DIR"
    
    echo "Files copied from $SOURCE_DIR to $DEST_DIR successfully."
fi