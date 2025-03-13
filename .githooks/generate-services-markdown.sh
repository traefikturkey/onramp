#!/usr/bin/bash

# Set the base URL for GitHub repository
GITHUB_BASE_URL="https://github.com/traefikturkey/onramp/tree/master/services-available"

# Initialize variables for services
declare -A services_map
service_count=0
alphabet=()

# Process each service file
for file in ./services-available/*.yml; do
  ((service_count++))
  service_name=$(basename "$file" .yml)
  service_link=$(sed -n '/^# \+https/p' "$file" | sed 's/^#\s*//g' | head -n 1)
  description=$(sed -n 's/^# \+description: //p' "$file" | head -n 1)
  initial=$(echo "$service_name" | head -c 1 | tr '[:lower:]' '[:upper:]')
  file_link="$GITHUB_BASE_URL/$service_name.yml"
  
  entry="- [$service_name]($file_link): $description"
  [ -n "$service_link" ] && entry="- [$service_name]($service_link) ([yml]($file_link)): $description"
  
  services_map["$initial"]+="$entry\n"
  [[ ! " ${alphabet[@]} " =~ " ${initial} " ]] && alphabet+=("$initial")
done

# Sort the alphabet array
IFS=$'\n' alphabet=($(sort <<<"${alphabet[*]}"))
unset IFS

# Initialize the SERVICES.md file
echo "# Available Services" > ./SERVICES.md
echo "$service_count services and counting..." >> ./SERVICES.md
echo "" >> ./SERVICES.md

# Create an index of letters for services
for letter in "${alphabet[@]}"; do
  echo "[$letter](#$letter)" >> ./SERVICES.md
done
echo "" >> ./SERVICES.md

# Append services to the SERVICES.md file under their corresponding letter
for initial in "${alphabet[@]}"; do
  echo "## $initial" >> ./SERVICES.md
  echo -e "${services_map[$initial]}" >> ./SERVICES.md
  echo "" >> ./SERVICES.md
done

# Initialize variables for games
declare -A games_map
game_count=0
game_alphabet=()

# Process each game file
for file in ./services-available/games/*.yml; do
  ((game_count++))
  service_name=$(basename "$file" .yml)
  service_link=$(sed -n '/^# \+https/p' "$file" | sed 's/^#\s*//g' | head -n 1)
  description=$(sed -n 's/^# \+description: //p' "$file" | head -n 1)
  initial=$(echo "$service_name" | head -c 1 | tr '[:lower:]' '[:upper:]')
  file_link="$GITHUB_BASE_URL/games/$service_name.yml"
  
  entry="- [$service_name]($file_link): $description"
  [ -n "$service_link" ] && entry="- [$service_name]($service_link) ([yml]($file_link)): $description"
  
  games_map["$initial"]+="$entry\n"
  [[ ! " ${game_alphabet[@]} " =~ " ${initial} " ]] && game_alphabet+=("$initial")
done

# Sort the game alphabet array
IFS=$'\n' game_alphabet=($(sort <<<"${game_alphabet[*]}"))
unset IFS

# Append a blank line and games header to the SERVICES.md file
echo "" >> ./SERVICES.md
echo "# Available Games" >> ./SERVICES.md
echo "$game_count games and counting..." >> ./SERVICES.md
echo "" >> ./SERVICES.md

# Create an index of letters for games
for letter in "${game_alphabet[@]}"; do
  echo "[$letter](#$letter-1)" >> ./SERVICES.md
done
echo "" >> ./SERVICES.md

# Append games to the SERVICES.md file under their corresponding letter
for initial in "${game_alphabet[@]}"; do
  echo "## $initial" >> ./SERVICES.md
  echo -e "${games_map[$initial]}" >> ./SERVICES.md
  echo "" >> ./SERVICES.md
done