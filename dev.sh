#!/usr/bin/env bash
# Source this file to get tlstart / tlstop dev helpers
# Usage: source /path/to/dev.sh

_TIMELOG_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

tlstart() {
    # Kill anything already on 8888
    kill "$(lsof -ti:8888)" 2>/dev/null
    tlserve &> /tmp/tlserve.log &
    echo $! > /tmp/tlserve.pid
    echo "API started on http://localhost:8888 (logs: /tmp/tlserve.log)"
    cd "$_TIMELOG_DIR/frontend" && npm run dev
}

tlstop() {
    if [[ -f /tmp/tlserve.pid ]]; then
        kill "$(cat /tmp/tlserve.pid)" 2>/dev/null && echo "API stopped"
        rm /tmp/tlserve.pid
    else
        kill "$(lsof -ti:8888)" 2>/dev/null && echo "API stopped"
    fi
}
