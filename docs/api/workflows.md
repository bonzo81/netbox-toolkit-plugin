# API Workflow Examples

This document provides focused examples of API workflows that leverage the unique capabilities not available through the web interface. For complete API documentation, see the [Commands API](../api/commands.md).

## Quick API Workflow Examples

### 1. Bulk Device Configuration

**Use Case**: Deploy configuration to multiple devices simultaneously

```bash
# Execute command across multiple devices
curl -X POST "https://netbox.example.com/api/plugins/toolkit/commands/bulk-execute/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "executions": [
      {
        "command_id": 5,
        "device_id": 101,
        "username": "admin",
        "password": "password",
        "variables": {"vlan_id": "100", "description": "Guest Network"}
      },
      {
        "command_id": 5,
        "device_id": 102,
        "username": "admin",
        "password": "password",
        "variables": {"vlan_id": "100", "description": "Guest Network"}
      }
    ]
  }'
```

### 2. Operational Statistics

**Use Case**: Get comprehensive network operations insights

```bash
# Get execution statistics
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/command-logs/statistics/"

# Export filtered logs
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/command-logs/export/?format=csv&start_date=2025-01-01"
```

### 3. Dynamic Variable Discovery

**Use Case**: Build dynamic interfaces based on actual NetBox data

```bash
# Get available variable choices for a specific device
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://netbox.example.com/api/plugins/toolkit/commands/1/variable-choices/?device_id=123"

# Execute with enhanced validation
curl -X POST "https://netbox.example.com/api/plugins/toolkit/commands/1/execute/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "device_id": 123,
    "username": "admin",
    "password": "password",
    "variables": {"interface_name": "GigabitEthernet0/1"}
  }'
```

## Integration Patterns

### Python Integration Example

```python
import requests

class NetBoxToolkitAPI:
    def __init__(self, base_url, token):
        self.base_url = f"{base_url}/api/plugins/toolkit"
        self.headers = {
            "Authorization": f"Token {token}",
            "Content-Type": "application/json"
        }

    def execute_command(self, command_id, device_id, credentials, variables=None):
        """Execute single command with optional variables"""
        payload = {
            "device_id": device_id,
            "username": credentials["username"],
            "password": credentials["password"],
            "variables": variables or {}
        }

        response = requests.post(
            f"{self.base_url}/commands/{command_id}/execute/",
            json=payload,
            headers=self.headers
        )
        return response.json()

    def bulk_execute(self, executions):
        """Execute multiple commands across multiple devices"""
        response = requests.post(
            f"{self.base_url}/commands/bulk-execute/",
            json={"executions": executions},
            headers=self.headers
        )
        return response.json()

    def get_statistics(self):
        """Get comprehensive execution statistics"""
        response = requests.get(
            f"{self.base_url}/command-logs/statistics/",
            headers=self.headers
        )
        return response.json()

# Usage
api = NetBoxToolkitAPI("https://netbox.example.com", "your-token")

# Single execution
result = api.execute_command(
    command_id=1,
    device_id=123,
    credentials={"username": "admin", "password": "password"},
    variables={"interface_name": "GigabitEthernet0/1"}
)

# Bulk execution
bulk_result = api.bulk_execute([
    {
        "command_id": 1,
        "device_id": 123,
        "username": "admin",
        "password": "password",
        "variables": {"interface_name": "GigabitEthernet0/1"}
    },
    {
        "command_id": 2,
        "device_id": 124,
        "username": "admin",
        "password": "password",
        "variables": {"vlan_id": "100"}
    }
])

# Get statistics
stats = api.get_statistics()
print(f"Success rate: {stats['success_rate']}%")
```

### Ansible Integration Example

```yaml
---
- name: NetBox Toolkit Command Execution
  hosts: localhost
  vars:
    netbox_url: "https://netbox.example.com"
    netbox_token: "{{ vault_netbox_token }}"

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
          username: "{{ device_username }}"
          password: "{{ device_password }}"
          variables:
            interface_name: "{{ interface_name }}"
      register: command_result

    - name: Display results
      debug:
        msg: "Command execution {{ 'successful' if command_result.json.success else 'failed' }}"
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any

    environment {
        NETBOX_TOKEN = credentials('netbox-api-token')
        NETBOX_URL = 'https://netbox.example.com'
    }

    stages {
        stage('Deploy VLAN Configuration') {
            steps {
                script {
                    def response = sh(
                        script: """
                        curl -s -X POST "${NETBOX_URL}/api/plugins/toolkit/commands/bulk-execute/" \
                          -H "Authorization: Token ${NETBOX_TOKEN}" \
                          -H "Content-Type: application/json" \
                          -d '${buildBulkExecutionPayload()}'
                        """,
                        returnStdout: true
                    )

                    def result = readJSON text: response

                    if (result.summary.failed > 0) {
                        error("Deployment failed on ${result.summary.failed} devices")
                    } else {
                        echo "Successfully deployed to ${result.summary.successful} devices"
                    }
                }
            }
        }
    }
}
```

## Advanced Automation Patterns

### 1. Configuration Drift Detection

Monitor and detect configuration changes across your network:

```python
def detect_configuration_drift():
    """Compare current configuration with baseline"""

    # Get baseline configurations from previous executions
    baseline_logs = api.export_logs(
        format="json",
        start_date="2025-01-01",
        command_name="show running-config"
    )

    # Execute current configuration checks
    current_results = api.bulk_execute(create_config_check_executions())

    # Compare and identify drift
    drift_analysis = compare_configurations(baseline_logs, current_results)

    return drift_analysis
```

### 2. Automated Compliance Reporting

Generate compliance reports with automatic remediation:

```python
def compliance_audit():
    """Run comprehensive compliance checks"""

    compliance_commands = [
        {"id": 10, "name": "NTP Check"},
        {"id": 11, "name": "SNMP Security"},
        {"id": 12, "name": "AAA Configuration"}
    ]

    # Execute compliance checks
    results = []
    for command in compliance_commands:
        result = api.bulk_execute(create_device_executions(command["id"]))
        results.append({
            "check": command["name"],
            "results": result
        })

    # Generate compliance report
    report = generate_compliance_report(results)

    # Trigger remediation for non-compliant devices
    if report["non_compliant_count"] > 0:
        trigger_remediation(report["non_compliant_devices"])

    return report
```

### 3. Performance Monitoring Integration

Integrate with monitoring systems for network performance tracking:

```python
def network_performance_monitoring():
    """Collect performance metrics for monitoring systems"""

    # Get interface utilization across all devices
    utilization_results = api.bulk_execute(
        create_interface_monitoring_executions()
    )

    # Get system health metrics
    health_results = api.bulk_execute(
        create_system_health_executions()
    )

    # Process and send to monitoring system
    metrics = process_performance_data(utilization_results, health_results)
    send_to_prometheus(metrics)  # or send_to_grafana, send_to_datadog, etc.

    return metrics
```

## Best Practices for API Integration

### 1. Error Handling
```python
def robust_command_execution(command_id, device_id, credentials, variables=None):
    """Execute command with proper error handling"""
    try:
        # Execute with enhanced validation (validation happens automatically)
        if variables:
            # Validation is now integrated into the execute endpoint

        # Execute command
        result = api.execute_command(command_id, device_id, credentials, variables)

        # Check for execution errors
        if not result["success"]:
            raise RuntimeError(f"Command execution failed: {result['error_message']}")

        # Check for syntax errors
        if result.get("syntax_error", {}).get("detected"):
            logging.warning(f"Syntax error detected: {result['syntax_error']}")

        return result

    except requests.exceptions.RequestException as e:
        logging.error(f"API request failed: {e}")
        raise
    except Exception as e:
        logging.error(f"Command execution error: {e}")
        raise
```

### 2. Rate Limiting and Retries
```python
import time
from functools import wraps

def retry_with_backoff(max_retries=3, backoff_factor=1):
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
                            time.sleep(wait_time)
                            continue
                    raise
            return None
        return wrapper
    return decorator

@retry_with_backoff(max_retries=3, backoff_factor=2)
def execute_with_retry(command_id, device_id, credentials):
    return api.execute_command(command_id, device_id, credentials)
```

### 3. Bulk Operation Optimization
```python
def optimized_bulk_execution(commands, devices, credentials):
    """Optimize bulk executions by batching and parallel processing"""

    # Create execution matrix
    executions = []
    for device in devices:
        for command in commands:
            executions.append({
                "command_id": command["id"],
                "device_id": device["id"],
                "username": credentials["username"],
                "password": credentials["password"],
                "variables": command.get("variables", {})
            })

    # Batch executions to avoid API limits
    batch_size = 50
    results = []

    for i in range(0, len(executions), batch_size):
        batch = executions[i:i + batch_size]
        batch_result = api.bulk_execute(batch)
        results.extend(batch_result["results"])

        # Add delay between batches to respect rate limits
        time.sleep(1)

    return results
```

For more comprehensive API examples and automation guides, see the [API Automation Examples](../api/automation-examples.md).