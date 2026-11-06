#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Stopping Nginx..."
if [ -f "$DIR/logs/nginx.pid" ] && kill -0 "$(cat "$DIR/logs/nginx.pid")" 2>/dev/null; then
    /home/linuxbrew/.linuxbrew/bin/nginx -p "$DIR" -c "$DIR/conf/nginx.conf" -s stop 2>/dev/null || true
fi

echo "Stopping Backend..."
"$DIR/backend/stop_backend.sh" 2>/dev/null || true

echo "All services stopped."
