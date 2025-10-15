# Device Credentials

This guide explains how to create and manage secure device credential in the NetBox Toolkit Plugin.

## Overview

Device Credential provide a secure way to store and manage network device credentials with:

- **Encrypted Storage**: All passwords are encrypted using Fernet encryption
- **Token-Based API Access**: Generate unique credential tokens for API operations
- **User Isolation**: Credential tokens are bound to specific users
- **Audit Trail**: All credential usage is logged for security compliance

## Creating Credential

### Step 1: Access Credential Management
1. Log in to your NetBox instance
2. Navigate to **Command Toolkit > Device Credential**
3. Click **"Add"** to create a new credential

### Step 2: Configure Credential Details
Fill in the credential information:

- **Name**: Descriptive name for the credential (e.g., "Core Routers - Admin", "Lab Switches - Readonly")
- **Description**: Optional notes about the credential purpose or scope
- **Platforms**: Select specific network platforms or leave blank to apply to all platforms
- **Username**: Device login username
- **Password**: Device login password

### Step 3: Save and Generate Token
1. Click **"Create"** to save the credential
2. The system will automatically generate a unique **Credential Token**
3. Copy the **Credential Token** for API usage

## Security Features

### Encryption
- All passwords are encrypted using **Fernet encryption**
- Each credential uses a unique encryption key
- Passwords are never stored in plain text

### Token-Based Access
- Each credential generates a unique **credential token**
- Tokens are used for API access to avoid transmitting usernames and passwords
- Tokens can be regenerated if compromised
- Tokens are bound to specific users for accountability

### Audit Logging
- All credential usage during command execution is logged with user attribution
- View credential usage history in command logs
- Track which users accessed which devices

## Using Credentials

### Web Interface Usage
1. When executing commands, you can either:
   - Select a stored credential from the dropdown, or
   - Enter device credentials manually in the execution form
2. The plugin will use the provided credentials securely

### API Integration
The API requires the use of credential tokens for enhanced security:

```bash
curl -X POST "https://netbox.example.com/api/plugins/toolkit/commands/17/execute/" \
  -H "Authorization: Token <your-netbox-api-token>" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 1,
    "credential_token": "<your-credential-token>"
  }'
```
