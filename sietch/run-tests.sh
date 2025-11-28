#!/usr/bin/env bash
# Run sietch unit tests
# Usage: ./sietch/run-tests.sh [pytest args...]

set -e

cd "$(dirname "$0")"

# Build and run tests
docker compose -f docker-compose.test.yml build --quiet
docker compose -f docker-compose.test.yml run --rm test "$@"
