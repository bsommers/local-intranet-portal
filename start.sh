#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "$DIR/logs"

# Start Python backend
echo "Starting Backend API on port 8081..."
"$DIR/backend/start_backend.sh"

# Start Nginx
echo "Starting Nginx on port 8088..."
if [ -f "$DIR/logs/nginx.pid" ] && kill -0 "$(cat "$DIR/logs/nginx.pid")" 2>/dev/null; then
    /home/linuxbrew/.linuxbrew/bin/nginx -p "$DIR" -c "$DIR/conf/nginx.conf" -s reload
else
    /home/linuxbrew/.linuxbrew/bin/nginx -p "$DIR" -c "$DIR/conf/nginx.conf"
fi

echo "================================================="
echo "Local Web Server is LIVE!"
echo "Local URL:   http://localhost:8088"
echo "Network URL: http://192.168.1.245:8088"
echo "API Gateway: http://192.168.1.245:8088/api/"
echo "================================================="
