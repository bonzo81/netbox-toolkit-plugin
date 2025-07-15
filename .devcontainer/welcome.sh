#!/bin/bash

echo ""
echo "Type 'netbox-start' to start the development server"
echo ""

# Check if we're in Codespaces or local development
if [ -n "$CODESPACES" ]; then
    echo "🌐 NetBox will be available via GitHub Codespaces port forwarding"
    echo "   Look for the auto-opened browser tab or check the 'Ports' panel"
    echo "   Port 8000 will be labeled 'NetBox Web Interface'"
else
    echo "📖 NetBox will be available at: http://localhost:8000"
fi

echo "🔐 Default login: admin / admin"
echo ""
echo "💡 Tip: Type 'dev-help' in any terminal to see all available commands"
echo ""
