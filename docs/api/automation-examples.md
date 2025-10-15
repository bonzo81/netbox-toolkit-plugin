# API Automation Examples

## Overview
This document provides practical examples of automating network operations using the NetBox Toolkit Plugin API. These examples leverage capabilities not available through the web interface.

## Prerequisites

- NetBox API token configured
- Device Credential Sets created with credential tokens
- Python requests library or equivalent API client

## Authentication Setup

```python
import requests

# Configuration
BASE_URL = "https://netbox.example.com"
API_TOKEN = "your-netbox-api-token"
CREDENTIAL_TOKEN = "your-credential-token"  # From Device Credential Set

headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}
```

## Network Monitoring Automation

### Automated Interface Monitoring

**Use Case**: Monitor interface status across all network devices every hour

```python
#!/usr/bin/env python3
"""Automated interface status monitoring"""

import requests
from datetime import datetime

def monitor_interfaces():
    # Get all active network devices
    devices_response = requests.get(
        f"{BASE_URL}/api/dcim/devices/",
        params={"status": "active"},
        headers=headers
    )
    devices = devices_response.json()["results"]

    # Get interface monitoring command
    commands_response = requests.get(
        f"{BASE_URL}/api/plugins/toolkit/commands/",
        params={"name__icontains": "interface status"},
        headers=headers
    )

    if not commands_response.json()["results"]:
        print("No interface status command found")
        return

    command_id = commands_response.json()["results"][0]["id"]

    # Execute on all devices
    executions = []
    for device in devices:
        executions.append({
            "command_id": command_id,
            "device_id": device["id"],
            "credential_token": CREDENTIAL_TOKEN
        })

    # Bulk execution
    bulk_response = requests.post(
        f"{BASE_URL}/api/plugins/toolkit/commands/bulk-execute/",
        json={"executions": executions},
        headers=headers
    )

    results = bulk_response.json()
    print(f"Monitoring complete: {results['summary']}")

    # Process failed executions
    for i, result in enumerate(results["results"]):
        if not result["success"]:
            device_name = devices[i]["name"]
            print(f"Failed on {device_name}: {result.get('error', 'Unknown error')}")

    return results

if __name__ == "__main__":
    results = monitor_interfaces()
```

### Device Health Monitoring

**Use Case**: Collect system health metrics for monitoring systems

```python
def collect_health_metrics():
    """Collect performance metrics for monitoring systems"""

    health_commands = [
        {"name": "show version", "metric": "system_info"},
        {"name": "show memory", "metric": "memory_usage"},
        {"name": "show cpu", "metric": "cpu_usage"},
        {"name": "show environment", "metric": "environmental"}
    ]

    # Get devices by role (e.g., core switches)
    devices_response = requests.get(
        f"{BASE_URL}/api/dcim/devices/",
        params={"role": "core-switch", "status": "active"},
        headers=headers
    )
    devices = devices_response.json()["results"]

    metrics = {}

    for command_info in health_commands:
        # Find command
        cmd_response = requests.get(
            f"{BASE_URL}/api/plugins/toolkit/commands/",
            params={"name__icontains": command_info["name"]},
            headers=headers
        )

        if not cmd_response.json()["results"]:
            continue

        command_id = cmd_response.json()["results"][0]["id"]

        # Execute on all core devices
        executions = [{
            "command_id": command_id,
            "device_id": device["id"],
            "credential_token": CREDENTIAL_TOKEN
        } for device in devices]

        result = requests.post(
            f"{BASE_URL}/api/plugins/toolkit/commands/bulk-execute/",
            json={"executions": executions},
            headers=headers
        )

        metrics[command_info["metric"]] = result.json()

    return metrics
```

## Configuration Management

### VLAN Deployment

**Use Case**: Deploy VLAN configurations to switch groups

```python
def deploy_vlan_config(vlan_id, switch_group, description):
    """Deploy VLAN configuration to a group of switches"""

    # Get switches in the specified group
    devices_response = requests.get(
        f"{BASE_URL}/api/dcim/devices/",
        params={"device_role__slug": switch_group, "status": "active"},
        headers=headers
    )
    devices = devices_response.json()["results"]

    # Get VLAN creation command
    commands_response = requests.get(
        f"{BASE_URL}/api/plugins/toolkit/commands/",
        params={"name": "Create VLAN"},
        headers=headers
    )

    if not commands_response.json()["results"]:
        raise Exception("VLAN creation command not found")

    command_id = commands_response.json()["results"][0]["id"]

    # Execute with enhanced validation (validation happens automatically in execute endpoint)
    # Variables will be validated as part of the execution process

    # Execute on all switches in group
    executions = []
    for device in devices:
        executions.append({
            "command_id": command_id,
            "device_id": device["id"],
            "credential_token": CREDENTIAL_TOKEN,
            "variables": {
                "vlan_id": str(vlan_id),
                "vlan_name": description
            }
        })

    # Deploy configuration
    deployment = requests.post(
        f"{BASE_URL}/api/plugins/toolkit/commands/bulk-execute/",
        json={"executions": executions},
        headers=headers
    )

    result = deployment.json()

    # Check for failures
    if result["summary"]["failed"] > 0:
        print(f"Deployment had {result['summary']['failed']} failures!")
        for i, exec_result in enumerate(result["results"]):
            if not exec_result["success"]:
                device_name = devices[i]["name"]
                print(f"Failed on {device_name}: {exec_result.get('error', 'Unknown error')}")

    return result

# Example usage
if __name__ == "__main__":
    result = deploy_vlan_config(
        vlan_id=100,
        switch_group="access-switch",
        description="Guest Network"
    )

    print(f"Deployment completed: {result['summary']['successful']} successful, {result['summary']['failed']} failed")
```

### Configuration Backup

**Use Case**: Automated configuration backup for all devices

```python
def backup_configurations():
    """Backup running configurations for all devices"""

    # Get all managed devices
    devices_response = requests.get(
        f"{BASE_URL}/api/dcim/devices/",
        params={"status": "active", "limit": 1000},
        headers=headers
    )
    devices = devices_response.json()["results"]

    # Get show running-config command
    commands_response = requests.get(
        f"{BASE_URL}/api/plugins/toolkit/commands/",
        params={"command__icontains": "show running-config"},
        headers=headers
    )

    backups = {}

    for command in commands_response.json()["results"]:
        # Get devices that match this command's platforms
        compatible_devices = [d for d in devices
                            if d.get("platform") and
                            any(p["id"] == d["platform"]["id"]
                                for p in command["platforms"])]

        if not compatible_devices:
            continue

        # Execute backup command
        executions = [{
            "command_id": command["id"],
            "device_id": device["id"],
            "credential_token": CREDENTIAL_TOKEN
        } for device in compatible_devices]

        result = requests.post(
            f"{BASE_URL}/api/plugins/toolkit/commands/bulk-execute/",
            json={"executions": executions},
            headers=headers
        )

        # Store successful backups
        for i, exec_result in enumerate(result.json()["results"]):
            if exec_result["success"]:
                device_name = compatible_devices[i]["name"]
                backups[device_name] = {
                    "timestamp": datetime.now().isoformat(),
                    "config": exec_result["output"]
                }

    return backups
```

## Compliance and Auditing

### Security Configuration Audit

**Use Case**: Automated compliance checking across network infrastructure

```python
def security_compliance_audit():
    """Run comprehensive security compliance checks"""

    compliance_checks = [
        {"command_name": "show ntp status", "check": "ntp_config"},
        {"command_name": "show snmp community", "check": "snmp_security"},
        {"command_name": "show aaa servers", "check": "aaa_config"}
    ]

    # Get all devices
    devices_response = requests.get(
        f"{BASE_URL}/api/dcim/devices/",
        params={"status": "active"},
        headers=headers
    )
    devices = devices_response.json()["results"]

    compliance_results = {
        "summary": {"total_devices": len(devices), "compliant": 0, "non_compliant": 0},
        "device_results": {},
        "violations": []
    }

    for check in compliance_checks:
        # Find command
        cmd_response = requests.get(
            f"{BASE_URL}/api/plugins/toolkit/commands/",
            params={"name__icontains": check["command_name"]},
            headers=headers
        )

        if not cmd_response.json()["results"]:
            continue

        command_id = cmd_response.json()["results"][0]["id"]

        # Execute compliance check
        executions = [{
            "command_id": command_id,
            "device_id": device["id"],
            "credential_token": CREDENTIAL_TOKEN
        } for device in devices]

        result = requests.post(
            f"{BASE_URL}/api/plugins/toolkit/commands/bulk-execute/",
            json={"executions": executions},
            headers=headers
        )

        # Analyze results (simplified - would need actual compliance logic)
        for i, exec_result in enumerate(result.json()["results"]):
            device_name = devices[i]["name"]

            if device_name not in compliance_results["device_results"]:
                compliance_results["device_results"][device_name] = {"checks": {}}

            if exec_result["success"]:
                # Analyze output for compliance (implementation specific)
                is_compliant = analyze_compliance_output(
                    exec_result["output"],
                    check["check"]
                )
                compliance_results["device_results"][device_name]["checks"][check["check"]] = is_compliant

                if not is_compliant:
                    compliance_results["violations"].append({
                        "device": device_name,
                        "check": check["check"],
                        "output": exec_result["output"][:200]  # Truncated
                    })

    return compliance_results

def analyze_compliance_output(output, check_type):
    """Analyze command output for compliance (simplified)"""
    # This would contain actual compliance checking logic
    # For demonstration purposes, always return True
    return True
```

## Error Handling Best Practices

### Robust Execution with Retry Logic

```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, backoff_factor=2):
    """Decorator for API calls with exponential backoff"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.HTTPError as e:
                    if e.response.status_code == 429:  # Rate limited
                        if attempt < max_retries - 1:
                            wait_time = backoff_factor * (2 ** attempt)
                            print(f"Rate limited, waiting {wait_time} seconds...")
                            time.sleep(wait_time)
                            continue
                    raise
            return None
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, backoff_factor=1)
def execute_command_with_retry(command_id, device_id):
    """Execute command with automatic retry on rate limits"""
    response = requests.post(
        f"{BASE_URL}/api/plugins/toolkit/commands/{command_id}/execute/",
        headers=headers,
        json={
            "device_id": device_id,
            "credential_token": CREDENTIAL_TOKEN
        }
    )
    response.raise_for_status()
    return response.json()
```

## Integration Examples

### Ansible Playbook Integration

```yaml
---
- name: NetBox Toolkit Command Execution
  hosts: localhost
  vars:
    netbox_url: "{{ netbox_base_url }}"
    netbox_token: "{{ vault_netbox_token }}"
    credential_token: "{{ vault_credential_token }}"

  tasks:
    - name: Execute interface status check
      uri:
        url: "{{ netbox_url }}/api/plugins/toolkit/commands/1/execute/"
        method: POST
        headers:
          Authorization: "Token {{ netbox_token }}"
          Content-Type: "application/json"
        body_format: json
        body:
          device_id: "{{ device_id }}"
          credential_token: "{{ credential_token }}"
          variables:
            interface_name: "{{ interface_name }}"
        status_code: 200
      register: command_result

    - name: Display results
      debug:
        msg: "Command execution {{ 'successful' if command_result.json.success else 'failed' }}"

    - name: Show command output
      debug:
        var: command_result.json.output
      when: command_result.json.success
```

## Related Documentation
- **Setup**: [Authentication Guide](auth.md)
- **Reference**: [Commands API](commands.md)
- **Authentication**: [Authentication & Permissions](auth.md)
- **Troubleshooting**: [Error Handling](errors.md)