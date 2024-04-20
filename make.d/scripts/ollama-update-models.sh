#!/bin/bash

file="etc/ollama/Ollamamodels"
parallel=""
use_docker=""
file_override=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --parallel)
        parallel="&"
        shift
        ;;
        --docker)
        docker_container=${2:-ollama} # Default to ollama if not provided as arg 2
        use_docker="docker exec $docker_container"
        shift
        ;;
        -f)
        file_override=true
        file="$2"
        shift 2
        ;;
        *)
        shift
        ;;
    esac
done

# Check if ollama command is in the path only if $use_docker is empty or not set
if [ -z "$use_docker" ]; then
    if ! command -v ollama &> /dev/null; then
        # Check if docker is running
        if docker info &> /dev/null; then
            echo "ollama command not found in path. Consider using the --docker flag."
        else
            echo "ollama command not found in path and docker is not running."
        fi
        exit 1
    fi
else
    if ! docker inspect "$docker_container" &> /dev/null; then
        echo "Error: Docker container $docker_container is not running."
        exit 1
    fi
fi

# Check if the Ollamamodels file exists
if [ ! -f "$file" ]; then
    echo "Error: $file not found." >&2
    exit 1
fi

# Get the list of installed models
installed_models=$($use_docker ollama list | awk 'NR>1 {print $1}')

# Read the Ollamamodels file and store the models in an array
declare -a models_in_file
while read -r line; do
    # Skip empty lines and lines starting with or containing only spaces
    if [[ -z "$line" || "$line" =~ ^[[:space:]]+$ || "$line" == "#"* ]]; then
        continue
    fi
    models_in_file+=("$line")
done < "$file"

# Find models that are installed but not in the file
models_to_remove=()
for model in $installed_models; do
    if ! [[ "${models_in_file[@]}" =~ "$model" ]]; then
        models_to_remove+=("$model")
    fi
done

# Ask the user if they want to remove the models
if [ ${#models_to_remove[@]} -gt 0 ]; then
    echo "The following models are installed but not in the Ollamamodels file:"
    for model in "${models_to_remove[@]}"; do
        echo "  * $model"
    done
    read -p "Do you want to remove these models? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for model in "${models_to_remove[@]}"; do
            $($use_docker ollama rm "$model")
        done
    fi
fi

# Pull models from the Ollamamodels file
index=1
total_count=$(wc -l < "$file")
while read -r line; do
    # Skip empty lines and lines starting with or containing only spaces
    if [[ -z "$line" || "$line" =~ ^[[:space:]]+$ || "$line" == "#"* ]]; then
        continue
    fi

    echo "Pulling model ($index/$total_count) $line"
    $($use_docker ollama pull "$line" $parallel)

    index=$((index + 1))
done < "$file"

# Wait for all the docker exec commands to finish
wait