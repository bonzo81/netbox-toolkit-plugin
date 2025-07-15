# GitHub Codespaces NetBox Configuration
# This file is automatically loaded when running in GitHub Codespaces
# to handle CSRF and networking configuration specific to Codespaces environment

import os

# GitHub Codespaces CSRF Configuration
# Handle dynamic Codespaces URLs for CSRF protection
codespace_name = os.environ.get('CODESPACE_NAME')
github_codespaces_port_forwarding_domain = os.environ.get('GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN', 'app.github.dev')

if codespace_name:
    # Construct the Codespaces URL
    codespaces_url = f"https://{codespace_name}-8000.{github_codespaces_port_forwarding_domain}"

    # Set CSRF trusted origins for Codespaces
    CSRF_TRUSTED_ORIGINS = [
        codespaces_url,
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]

    # Also set allowed hosts for Codespaces
    ALLOWED_HOSTS = [
        f"{codespace_name}-8000.{github_codespaces_port_forwarding_domain}",
        'localhost',
        '127.0.0.1',
        '*',  # Allow all hosts for development
    ]

    print(f"🔗 Codespaces detected: {codespace_name}")
    print(f"🔒 CSRF Trusted Origins: {CSRF_TRUSTED_ORIGINS}")
    print(f"🌐 Allowed Hosts: {ALLOWED_HOSTS}")
else:
    # Fallback configuration for Codespaces without proper environment detection
    print("⚠️  Codespaces detected but CODESPACE_NAME not found")
    CSRF_TRUSTED_ORIGINS = [
        'http://localhost:8000',
        'http://127.0.0.1:8000',
    ]
    ALLOWED_HOSTS = ['*']  # Allow all hosts for development
