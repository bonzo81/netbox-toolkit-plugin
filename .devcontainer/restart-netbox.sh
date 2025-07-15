#!/bin/bash

echo "🔄 Restarting NetBox to apply configuration changes..."

# Stop any running NetBox instance
if [ -f /tmp/netbox.pid ]; then
    PID=$(cat /tmp/netbox.pid)
    if kill -0 $PID 2>/dev/null; then
        echo "🛑 Stopping NetBox (PID: $PID)"
        kill $PID
        sleep 2
    fi
    rm -f /tmp/netbox.pid
fi

# Kill any remaining runserver processes
pkill -f "manage.py runserver" 2>/dev/null || true

echo "⏳ Waiting for processes to stop..."
sleep 3

# Start NetBox again in background
echo "🚀 Starting NetBox..."
/workspaces/netbox-toolkit-plugin/.devcontainer/start-netbox.sh --background

echo "✅ NetBox restart complete!"
