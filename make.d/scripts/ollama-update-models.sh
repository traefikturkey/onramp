#!/bin/bash

file="etc/ollama/Ollamamodels"
parallel=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --parallel)
        parallel=true
        shift
        ;;
        *)
        shift
        ;;
    esac
done

# Check if the Ollamamodels file exists
if [ ! -f "$file" ]; then
    echo "Error: $file not found." >&2
    exit 1
fi

# Count the total number of models
total_count=$(wc -l < "$file")

index=1
while read -r line; do
    # Skip empty lines and lines starting with or containing only spaces
    if [[ -z "$line" || "$line" =~ ^[[:space:]]+$ || "$line" == "#"* ]]; then
        continue
    fi

    echo "Pulling model ($index/$total_count) $line"
    if $parallel; then
        docker exec ollama ollama pull "$line" &
    else
        docker exec ollama ollama pull "$line"
    fi

    index=$((index + 1))
done < "$file"

# Wait for all the docker exec commands to finish
wait