#!/usr/bin/env bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PID_FILE="$DIR/../logs/backend.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
    echo "Backend already running (PID: $(cat "$PID_FILE"))"
    exit 0
fi

/home/linuxbrew/.linuxbrew/bin/python3 "$DIR/server.py" >> "$DIR/../logs/backend.log" 2>&1 &
PID=$!
echo $PID > "$PID_FILE"
echo "Backend started on port 8081 (PID: $PID)"
