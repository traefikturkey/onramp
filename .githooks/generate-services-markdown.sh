#!/usr/bin/bash

services=""
service_count=0
for file in ./services-available/*.yml; do
  ((service_count++))
  service_name=$(basename "$file" .yml)
  service_link=$(sed -n '/^# \+https/p' "$file" | sed 's/^#\s*//g' | head -n 1)
  description=$(sed -n 's/^# \+description: //p' "$file" | head -n 1)
  if [ -n "$service_link" ]; then
      services="$services\n- [$service_name]($service_link): $description"
  else
      services="$services\n- $service_name: $description"
  fi
done
echo "# Available Services" > ./SERVICES.md
echo "$service_count services and counting..." >> ./SERVICES.md
echo "" >> ./SERVICES.md
echo -e "$services" >> ./SERVICES.md

games=""
game_count=0
for file in ./services-available/games/*.yml; do
  ((game_count++))
  service_name=$(basename "$file" .yml)
  service_link=$(sed -n '/^# \+https/p' "$file" | sed 's/^#\s*//g' | head -n 1)
  description=$(sed -n 's/^# \+description: //p' "$file" | head -n 1)
  if [ -n "$service_link" ]; then
      games="$games\n- [$service_name]($service_link): $description"
  else
      games="$games\n- $service_name: $description"
  fi
done
echo "" >> ./SERVICES.md
echo "# Available Games" >> ./SERVICES.md
echo "$game_count games and counting..." >> ./SERVICES.md
echo "" >> ./SERVICES.md
echo -e "$games" >> ./SERVICES.md