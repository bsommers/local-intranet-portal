#!/usr/bin/env bash
set -e

# Start Python backend
echo "Starting Python API on port 8081..."
python3 /app/backend/server.py &
BACKEND_PID=$!

# Trap signals for clean shutdown
trap "kill -TERM $BACKEND_PID; nginx -s quit; exit 0" SIGINT SIGTERM

echo "Starting Nginx on port 8088..."
nginx -g "daemon off;"
