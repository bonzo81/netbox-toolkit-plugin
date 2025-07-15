#!/bin/bash

set -e

echo "🚀 Setting up NetBox Toolkit Plugin development environment..."
echo "📍 Current working directory: $(pwd)"
echo "📍 Current user: $(whoami)"

# Set NetBox version from environment variable (default to latest if not set)
NETBOX_VERSION=${NETBOX_VERSION:-"latest"}

echo "📦 Using NetBox Docker image: netboxcommunity/netbox:${NETBOX_VERSION}"

# Check if we're running as root and find the correct setup
if [ "$EUID" -eq 0 ]; then
    echo "🔍 Running as root - setting up environment..."
fi

# Verify NetBox virtual environment exists
if [ ! -f "/opt/netbox/venv/bin/activate" ]; then
    echo "❌ NetBox virtual environment not found at /opt/netbox/venv/"
    echo "This might indicate an issue with the NetBox Docker image."
    exit 1
fi

# Activate NetBox virtual environment
echo "🐍 Activating NetBox virtual environment..."
source /opt/netbox/venv/bin/activate

echo "🔧 Installing development dependencies..."
apt-get update -qq
apt-get install -y -qq net-tools
uv pip install pytest pytest-django ruff

echo "📦 Installing plugin in development mode..."
cd /workspaces/netbox-toolkit-plugin
uv pip install -e .

echo "⚙️ Configuring NetBox for plugin development..."

# Ensure config directory exists
mkdir -p /etc/netbox/config

# Install extra packages if extra-requirements.txt exists
if [ -f /workspaces/netbox-toolkit-plugin/.devcontainer/extra-requirements.txt ]; then
    echo "📦 Installing extra packages from extra-requirements.txt..."
    uv pip install -r /workspaces/netbox-toolkit-plugin/.devcontainer/extra-requirements.txt
fi

# Create plugin configuration file (for reference/future use)
cat > /etc/netbox/config/plugins.py << 'EOF'
"""
NetBox Toolkit Plugin Configuration

This file is created for reference but the actual plugin configuration
is added directly to the main NetBox configuration.py file.

You can use this file for more complex plugin configurations in the future.
"""

# Plugin configuration (for reference)
PLUGINS = [
    'netbox_toolkit_plugin',
]

PLUGINS_CONFIG = {
    'netbox_toolkit_plugin': {
        'device_ext_page': 'right',
    }
}
EOF

# Check if main configuration exists and add plugin settings directly
if [ -f /etc/netbox/config/configuration.py ]; then
    # Base toolkit plugin configuration
    if ! grep -q "netbox_toolkit_plugin" /etc/netbox/config/configuration.py 2>/dev/null; then
        echo "" >> /etc/netbox/config/configuration.py
        echo "# NetBox Toolkit Plugin Configuration" >> /etc/netbox/config/configuration.py
        echo "PLUGINS = PLUGINS + ['netbox_toolkit_plugin'] if 'PLUGINS' in locals() else ['netbox_toolkit_plugin']" >> /etc/netbox/config/configuration.py
        echo "PLUGINS_CONFIG = PLUGINS_CONFIG if 'PLUGINS_CONFIG' in locals() else {}" >> /etc/netbox/config/configuration.py
        echo "PLUGINS_CONFIG['netbox_toolkit_plugin'] = {" >> /etc/netbox/config/configuration.py
        echo "    'device_ext_page': 'right'," >> /etc/netbox/config/configuration.py
        echo "}" >> /etc/netbox/config/configuration.py
    fi

    # Add extra plugins if extra-plugins.py exists
    if [ -f /workspaces/netbox-toolkit-plugin/.devcontainer/extra-plugins.py ]; then
        echo "🔌 Adding extra plugins from extra-plugins.py..."
        if ! grep -q "# Extra Plugins Configuration" /etc/netbox/config/configuration.py 2>/dev/null; then
            echo "" >> /etc/netbox/config/configuration.py
            echo "# Extra Plugins Configuration" >> /etc/netbox/config/configuration.py
            cat /workspaces/netbox-toolkit-plugin/.devcontainer/extra-plugins.py >> /etc/netbox/config/configuration.py
            echo "✅ Added extra plugins configuration"
        else
            echo "✅ Extra plugins configuration already exists"
        fi
    fi

    # Add extra configuration if extra-configuration.py exists
    if [ -f /workspaces/netbox-toolkit-plugin/.devcontainer/extra-configuration.py ]; then
        echo "⚙️ Adding extra configuration from extra-configuration.py..."
        if ! grep -q "# Extra NetBox Configuration" /etc/netbox/config/configuration.py 2>/dev/null; then
            echo "" >> /etc/netbox/config/configuration.py
            echo "# Extra NetBox Configuration" >> /etc/netbox/config/configuration.py
            cat /workspaces/netbox-toolkit-plugin/.devcontainer/extra-configuration.py >> /etc/netbox/config/configuration.py
            echo "✅ Added extra NetBox configuration"
        else
            echo "✅ Extra NetBox configuration already exists"
        fi
    fi

    if grep -q "netbox_toolkit_plugin" /etc/netbox/config/configuration.py 2>/dev/null; then
        echo "✅ Plugin configuration exists in NetBox settings"
    fi
else
    echo "⚠️  Warning: /etc/netbox/config/configuration.py not found"
    echo "Plugin configuration may need to be added manually"
fi

echo "🗄️ Running database migrations..."
cd /opt/netbox/netbox

# Check database connectivity first
echo "🔍 Checking database connectivity..."
for i in {1..30}; do
    if DJANGO_SETTINGS_MODULE=netbox.settings SECRET_KEY="${SECRET_KEY:-dummydummydummydummydummydummydummydummydummydummydummydummy}" DEBUG="${DEBUG:-True}" python -c "
import django
django.setup()
from django.db import connection
try:
    connection.ensure_connection()
    print('✅ Database connection successful')
except Exception as e:
    print(f'⏳ Database not ready yet (attempt {i}/30): {e}')
    exit(1)
" 2>/dev/null | grep -v "🧬 loaded config"; then
        echo "✅ Database is ready!"
        break
    else
        echo "⏳ Waiting for database... (attempt $i/30)"
        sleep 2
    fi

    if [ $i -eq 30 ]; then
        echo "❌ Database connection failed after 30 attempts"
        echo "🔍 Checking database service status..."
        # Continue anyway - let migrations handle the error
        echo "⚠️ Proceeding with migrations despite connectivity issues..."
    fi
done

# Ensure SECRET_KEY is set for migration
export SECRET_KEY="${SECRET_KEY:-dummydummydummydummydummydummydummydummydummydummydummydummy}"
export DEBUG="${DEBUG:-True}"
echo "🗃️  Applying database migrations..."
python manage.py migrate 2>&1 | grep -v "🧬 loaded config" | grep -E "(Operations to perform|Running migrations|Apply all migrations|No migrations to apply|\s+Applying|\s+OK)"

echo "🔐 Creating superuser (if not exists)..."
# The superuser should be created automatically by the NetBox Docker image
# but we'll check and create one if needed
DEBUG="${DEBUG:-True}" SECRET_KEY="${SECRET_KEY:-dummydummydummydummydummydummydummydummydummydummydummydummy}" \
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
username = '${SUPERUSER_NAME:-admin}'
email = '${SUPERUSER_EMAIL:-admin@example.com}'
password = '${SUPERUSER_PASSWORD:-admin}'
if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Created superuser: {username}/{password}')
else:
    print(f'Superuser {username} already exists')
" 2>&1 | grep -v "🧬 loaded config"

echo "📊 Collecting static files..."
DEBUG="${DEBUG:-True}" SECRET_KEY="${SECRET_KEY:-dummydummydummydummydummydummydummydummydummydummydummydummy}" \
python manage.py collectstatic --noinput 2>&1 | grep -v "🧬 loaded config"

echo "📝 Setting up development scripts..."

# Make start-netbox.sh executable (file already exists in repository)
chmod +x /workspaces/netbox-toolkit-plugin/.devcontainer/start-netbox.sh

echo "📋 Creating useful aliases..."
cat >> ~/.bashrc << EOF
# NetBox Toolkit Plugin Development Aliases
export PATH="/opt/netbox/venv/bin:\$PATH"
export SECRET_KEY="\${SECRET_KEY:-dummydummydummydummydummydummydummydummydummydummydummydummy}"
export DEBUG="\${DEBUG:-True}"
alias netbox-start="/workspaces/netbox-toolkit-plugin/.devcontainer/start-netbox.sh --background"
alias netbox-run="/workspaces/netbox-toolkit-plugin/.devcontainer/start-netbox.sh"
alias netbox-restart="netbox-stop && sleep 1 && netbox-start"
alias netbox-reload="cd /workspaces/netbox-toolkit-plugin && uv pip install -e . && netbox-restart"
alias netbox-stop="[ -f /tmp/netbox.pid ] && kill \$(cat /tmp/netbox.pid) && rm /tmp/netbox.pid && echo 'NetBox stopped' || echo 'NetBox not running'"
alias netbox-logs="tail -f /tmp/netbox.log"
alias netbox-status="[ -f /tmp/netbox.pid ] && kill -0 \$(cat /tmp/netbox.pid) 2>/dev/null && echo 'NetBox is running (PID: '\$(cat /tmp/netbox.pid)')' || echo 'NetBox is not running'"
alias netbox-shell="cd /opt/netbox/netbox && source /opt/netbox/venv/bin/activate && python manage.py shell"
alias netbox-test="cd /workspaces/netbox-toolkit-plugin && source /opt/netbox/venv/bin/activate && python -m pytest"
alias netbox-manage="cd /opt/netbox/netbox && source /opt/netbox/venv/bin/activate && python manage.py"
alias plugin-install="cd /workspaces/netbox-toolkit-plugin && uv pip install -e ."
alias ruff-check="cd /workspaces/netbox-toolkit-plugin && ruff check ."
alias ruff-format="cd /workspaces/netbox-toolkit-plugin && ruff format ."
alias ruff-fix="cd /workspaces/netbox-toolkit-plugin && ruff check --fix ."
alias diagnose="/workspaces/netbox-toolkit-plugin/.devcontainer/diagnose.sh"

# Alias to show all available aliases
alias dev-help='echo "🎯 NetBox Toolkit Plugin Development Commands:"; echo ""; echo "📊 NetBox Server Management:"; echo "  netbox-start        : Start NetBox in background"; echo "  netbox-run          : Start NetBox in foreground (for debugging)"; echo "  netbox-stop         : Stop NetBox background server"; echo "  netbox-restart      : Restart NetBox (stop + start)"; echo "  netbox-reload       : Reinstall plugin and restart NetBox"; echo "  netbox-status       : Check if NetBox is running"; echo "  netbox-logs         : View NetBox server logs"; echo ""; echo "🛠️  Development Tools:"; echo "  netbox-shell        : Open NetBox Django shell"; echo "  netbox-test         : Run plugin tests"; echo "  netbox-manage       : Run Django management commands"; echo "  plugin-install      : Reinstall plugin in development mode"; echo ""; echo "🔧 Code Quality:"; echo "  ruff-check          : Check code with Ruff"; echo "  ruff-format         : Format code with Ruff"; echo "  ruff-fix            : Auto-fix code issues with Ruff"; echo ""; echo "🔍 Diagnostics:"; echo "  diagnose            : Run startup diagnostics"; echo "  dev-help            : Show this help message"; echo ""; echo "📖 NetBox available at: http://localhost:8000 (admin/admin)"; echo ""'

# Show brief help message on every new terminal
echo ""
echo "💡 NetBox Toolkit Plugin dev commands available! Type 'dev-help' to see all commands."
echo ""
EOF

echo "🧪 Testing plugin installation..."
cd /opt/netbox/netbox
if python -c "import netbox_toolkit_plugin; print('✅ Plugin import successful')" 2>&1 | grep -v "🧬 loaded config" | grep -q "✅ Plugin import successful"; then
    echo "✅ Plugin is properly installed and importable"
else
    echo "⚠️  Warning: Plugin may not be properly installed"
fi

echo "🚀 NetBox Toolkit Plugin Dev Environment Ready!"
