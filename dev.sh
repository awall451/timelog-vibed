#!/usr/bin/env bash
# Source this file to get tlstart / tlstop and CLI helpers
# Usage: source /path/to/dev.sh

_TIMELOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

tlstart() {
    docker compose -f "$_TIMELOG_DIR/docker-compose.yml" up --build -d
    echo "Timelog running at http://localhost:3000"
    echo "API available at  http://localhost:8888"
}

tlstop() {
    docker compose -f "$_TIMELOG_DIR/docker-compose.yml" down
}

# CLI wrappers — run commands inside the API container
tlshow()   { docker compose -f "$_TIMELOG_DIR/docker-compose.yml" exec api tlshow "$@"; }
tlsum()    { docker compose -f "$_TIMELOG_DIR/docker-compose.yml" exec api tlsum "$@"; }
tlexport() {
    local filename="timelog-$(date +%Y-%m-%d).csv"
    docker compose -f "$_TIMELOG_DIR/docker-compose.yml" exec api tlexport
    docker compose -f "$_TIMELOG_DIR/docker-compose.yml" cp "api:/app/$filename" "./$filename"
    echo "Saved to $(pwd)/$filename"
}
tlhelp()   { docker compose -f "$_TIMELOG_DIR/docker-compose.yml" exec api tlhelp "$@"; }
tlupdate() { docker compose -f "$_TIMELOG_DIR/docker-compose.yml" exec -it api tlupdate "$@"; }
