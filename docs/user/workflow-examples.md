# Workflow Examples

This guide provides practical examples of how to use the NetBox Toolkit Plugin in real-world scenarios. We'll cover both web interface (GUI) and API workflows, from basic operations to advanced automation scenarios.

## Web Interface Workflows

The web interface is ideal for interactive command execution, testing, and command development. Here are the most common workflows.

### Workflow 1: Quick Device Troubleshooting

**Scenario**: A network engineer needs to quickly diagnose interface issues on a specific switch.

**Steps**:
1. **Navigate to Device**: Go to the device page in NetBox (e.g., `switch01.example.com`)
2. **Access Toolkit Tab**: Click the "Toolkit" tab to access network commands
3. **Select Command**: Choose "Show Interface Status" from the available commands
4. **Configure Variables**:
   - Click "Execute" to open the command modal
   - Select the problematic interface from the dropdown (e.g., `GigabitEthernet0/1`)
   - Enter device credentials
5. **Execute & Review**:
   - Click "Run Command"
   - Review the parsed output in the structured table format
   - Check for interface status, errors, or configuration issues
6. **Export if Needed**: Use the "Export CSV" button to save parsed data for reporting

**Benefits**:
- Visual interface selection with NetBox data validation
- Real-time parsing and structured output display
- Immediate error detection with syntax guidance
- Easy export for documentation

### Workflow 2: Configuration Validation Across Device Types

**Scenario**: A network administrator needs to verify VLAN configurations across different switch models.

**Steps**:
1. **Create Variable Command**:
   - Navigate to Commands → Add Command
   - Name: "Show VLAN Configuration"
   - Command: `show vlan id <vlan_id>`
   - Add variable: `vlan_id` (type: NetBox VLAN)
2. **Test on Multiple Devices**:
   - Visit each switch device page → Toolkit tab
   - Execute the command with different VLAN IDs
   - Compare output formats and data across device platforms
3. **Review Command History**:
   - Navigate to Command Logs to review all executions
   - Filter by command name to see all VLAN checks
   - Export individual results as needed

**Benefits**:
- Single command definition works across multiple device types
- NetBox data integration ensures valid VLAN selections
- Command history provides audit trail
- Platform-specific output parsing

### Workflow 3: Interactive Command Development

**Scenario**: Creating and testing a new command template with variables.

**Steps**:
1. **Command Creation**:
   - Commands → Add Command
   - Start with basic command: `show ip route <destination>`
   - Define variable: `destination` (type: text)
   - Set platforms and command type
2. **Testing Phase**:
   - Use device Toolkit tab to test command
   - Try various destination values (IP addresses, networks)
   - Verify output parsing works correctly
3. **Refinement**:
   - Edit command to improve variable validation
   - Add help text and default values
   - Test edge cases and error handling
4. **Production Ready**:
   - Command is now available across all compatible devices
   - Other users can execute with guided variable selection

**Benefits**:
- Interactive testing environment
- Real-time feedback on command syntax and variables
- Immediate validation of NetBox data integration
- Collaborative command development

## API Workflows

The API enables automation, bulk operations, and integration scenarios not possible through the web interface.

### Workflow 4: Automated Interface Monitoring

**Scenario**: Automated system needs to monitor interface status across all network devices every hour.

**Implementation**:
```python
#!/usr/bin/env python3
"""Automated interface status monitoring"""

import requests
from datetime import datetime

NETBOX_URL = "https://netbox.example.com"
API_TOKEN = "your-api-token-here"

headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

def monitor_interfaces():
    # Get all network devices
    devices_response = requests.get(f"{NETBOX_URL}/api/dcim/devices/", headers=headers)
    devices = devices_response.json()["results"]

    # Get interface monitoring command
    commands_response = requests.get(
        f"{NETBOX_URL}/api/plugins/toolkit/commands/",
        params={"name__icontains": "interface status"},
        headers=headers
    )
    command_id = commands_response.json()["results"][0]["id"]

    # Execute on all devices
    executions = []
    for device in devices:
        if device["status"]["value"] == "active":
            executions.append({
                "command_id": command_id,
                "device_id": device["id"],
                "username": "monitoring",
                "password": "secure-password",
                "variables": {}  # No variables for general status
            })

    # Bulk execution
    bulk_response = requests.post(
        f"{NETBOX_URL}/api/plugins/toolkit/commands/bulk-execute/",
        json={"executions": executions},
        headers=headers
    )

    results = bulk_response.json()
    print(f"Monitoring complete: {results['summary']}")

    return results

if __name__ == "__main__":
    results = monitor_interfaces()
```

**Benefits**:
- Automated execution across entire infrastructure
- Bulk operations reduce API calls and execution time
- Structured results for further processing
- Integration with monitoring systems

### Workflow 5: Configuration Deployment Pipeline

**Scenario**: Deploy VLAN configurations to specific switch groups as part of a CI/CD pipeline.

**Implementation**:
```python
#!/usr/bin/env python3
"""VLAN configuration deployment"""

import requests
import json

def deploy_vlan_config(vlan_id, switch_group, description):
    """Deploy VLAN configuration to a group of switches"""

    # Get switches in the specified group
    devices = requests.get(
        f"{NETBOX_URL}/api/dcim/devices/",
        params={"device_role__slug": switch_group},
        headers=headers
    ).json()["results"]

    # Get VLAN creation command
    commands = requests.get(
        f"{NETBOX_URL}/api/plugins/toolkit/commands/",
        params={"name": "Create VLAN"},
        headers=headers
    ).json()["results"]

    if not commands:
        raise Exception("VLAN creation command not found")

    command_id = commands[0]["id"]

    # Validate variables first
    validation_payload = {
        "variables": {
            "vlan_id": str(vlan_id),
            "vlan_name": description
        }
    }

    validation = requests.post(
        f"{NETBOX_URL}/api/plugins/toolkit/commands/{command_id}/validate-variables/",
        json=validation_payload,
        headers=headers
    )

    if validation.status_code != 200:
        raise Exception(f"Variable validation failed: {validation.json()}")

    # Execute on all switches in group
    executions = []
    for device in devices:
        executions.append({
            "command_id": command_id,
            "device_id": device["id"],
            "username": "automation",
            "password": "secure-password",
            "variables": {
                "vlan_id": str(vlan_id),
                "vlan_name": description
            }
        })

    # Deploy configuration
    deployment = requests.post(
        f"{NETBOX_URL}/api/plugins/toolkit/commands/bulk-execute/",
        json={"executions": executions},
        headers=headers
    )

    return deployment.json()

# Example usage in CI/CD pipeline
if __name__ == "__main__":
    result = deploy_vlan_config(
        vlan_id=100,
        switch_group="access-switch",
        description="Guest Network"
    )

    if result["summary"]["failed"] > 0:
        print("Deployment had failures!")
        exit(1)
    else:
        print("Deployment successful!")
```

**Benefits**:
- Automated configuration deployment
- Pre-deployment validation prevents errors
- Rollback capabilities through command logs
- Integration with existing CI/CD tools

### Workflow 6: Advanced Operational Analytics

**Scenario**: Generate comprehensive network operations reports combining execution statistics with custom analysis.

**Implementation**:
```python
#!/usr/bin/env python3
"""Advanced operational analytics and reporting"""

import requests
import pandas as pd
from datetime import datetime, timedelta

def generate_operations_report():
    """Generate comprehensive operations report"""

    # Get execution statistics
    stats = requests.get(
        f"{NETBOX_URL}/api/plugins/toolkit/command-logs/statistics/",
        headers=headers
    ).json()

    # Get detailed logs for last 30 days
    thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    logs = requests.get(
        f"{NETBOX_URL}/api/plugins/toolkit/command-logs/export/",
        params={
            "format": "json",
            "start_date": thirty_days_ago
        },
        headers=headers
    ).json()

    # Create DataFrame for analysis
    df = pd.DataFrame(logs["results"])

    # Advanced analytics
    analysis = {
        "overview": {
            "total_executions": stats["total_logs"],
            "success_rate": stats["success_rate"],
            "last_30_days": len(df)
        },
        "device_analysis": {
            "most_active_devices": df.groupby("device")["id"].count().head(10).to_dict(),
            "problematic_devices": df[df["success"] == False].groupby("device")["id"].count().head(5).to_dict()
        },
        "command_patterns": {
            "top_commands": stats["top_commands"],
            "failure_patterns": stats["common_errors"]
        },
        "temporal_analysis": {
            "daily_volume": df.groupby(df["created"].str[:10])["id"].count().to_dict(),
            "hourly_patterns": df.groupby(df["created"].str[11:13])["id"].count().to_dict()
        }
    }

    return analysis

def create_dashboard_data():
    """Create data for operational dashboard"""
    analysis = generate_operations_report()

    # Format for dashboard consumption
    dashboard_data = {
        "kpis": [
            {"metric": "Success Rate", "value": f"{analysis['overview']['success_rate']:.1f}%"},
            {"metric": "30-Day Executions", "value": analysis['overview']['last_30_days']},
            {"metric": "Total Commands", "value": len(analysis['command_patterns']['top_commands'])}
        ],
        "alerts": [],
        "trends": analysis["temporal_analysis"]
    }

    # Generate alerts for operational issues
    if analysis['overview']['success_rate'] < 90:
        dashboard_data['alerts'].append({
            "severity": "warning",
            "message": f"Success rate below 90%: {analysis['overview']['success_rate']:.1f}%"
        })

    return dashboard_data

if __name__ == "__main__":
    report = generate_operations_report()
    print(json.dumps(report, indent=2))
```

**Benefits**:
- Advanced analytics not available through GUI
- Integration with business intelligence tools
- Automated report generation
- Proactive issue identification

## API-Exclusive Advanced Workflow: Network Compliance Automation

**Scenario**: Automated compliance checking across the entire network infrastructure with remediation workflows.

**Implementation**:
```python
#!/usr/bin/env python3
"""Network compliance automation framework"""

import requests
import json
from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class ComplianceCheck:
    name: str
    command_id: int
    validation_rules: Dict[str, Any]
    remediation_command_id: int = None

class NetworkComplianceFramework:
    def __init__(self, netbox_url: str, api_token: str):
        self.base_url = f"{netbox_url}/api/plugins/toolkit"
        self.headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

    def run_compliance_suite(self, device_group: str) -> Dict:
        """Run full compliance check suite on device group"""

        # Define compliance checks
        checks = [
            ComplianceCheck(
                name="NTP Configuration",
                command_id=self.get_command_id("show ntp status"),
                validation_rules={"synchronized": True, "servers": {"min_count": 2}},
                remediation_command_id=self.get_command_id("configure ntp servers")
            ),
            ComplianceCheck(
                name="SNMP Security",
                command_id=self.get_command_id("show snmp community"),
                validation_rules={"public_community": False, "v3_enabled": True}
            ),
            ComplianceCheck(
                name="AAA Configuration",
                command_id=self.get_command_id("show aaa servers"),
                validation_rules={"radius_servers": {"min_count": 1}, "local_fallback": True}
            )
        ]

        # Get devices in group
        devices = self.get_device_group(device_group)

        compliance_results = {
            "summary": {"total_devices": len(devices), "compliant": 0, "non_compliant": 0},
            "device_results": {},
            "remediation_actions": []
        }

        # Run compliance checks
        for check in checks:
            results = self.execute_compliance_check(check, devices)

            for device_id, result in results.items():
                if device_id not in compliance_results["device_results"]:
                    compliance_results["device_results"][device_id] = {"checks": {}, "overall_compliant": True}

                compliance_results["device_results"][device_id]["checks"][check.name] = result

                if not result["compliant"]:
                    compliance_results["device_results"][device_id]["overall_compliant"] = False

                    # Queue remediation if available
                    if check.remediation_command_id:
                        compliance_results["remediation_actions"].append({
                            "device_id": device_id,
                            "check": check.name,
                            "command_id": check.remediation_command_id,
                            "issues": result["issues"]
                        })

        # Calculate summary
        for device_result in compliance_results["device_results"].values():
            if device_result["overall_compliant"]:
                compliance_results["summary"]["compliant"] += 1
            else:
                compliance_results["summary"]["non_compliant"] += 1

        return compliance_results

    def execute_compliance_check(self, check: ComplianceCheck, devices: List[Dict]) -> Dict:
        """Execute a specific compliance check across devices"""

        # Bulk execute compliance command
        executions = [
            {
                "command_id": check.command_id,
                "device_id": device["id"],
                "username": "compliance",
                "password": "secure-password",
                "variables": {}
            }
            for device in devices
        ]

        response = requests.post(
            f"{self.base_url}/commands/bulk-execute/",
            json={"executions": executions},
            headers=self.headers
        )

        results = {}
        for i, result in enumerate(response.json()["results"]):
            device_id = devices[i]["id"]

            if result["success"]:
                # Get command log for detailed analysis
                log_data = self.get_command_log(result["command_log_id"])
                compliance_result = self.validate_compliance(log_data, check.validation_rules)
            else:
                compliance_result = {
                    "compliant": False,
                    "issues": [f"Command execution failed: {result.get('error', 'Unknown error')}"]
                }

            results[device_id] = compliance_result

        return results

    def execute_remediation(self, remediation_actions: List[Dict]) -> Dict:
        """Execute remediation actions for compliance violations"""

        if not remediation_actions:
            return {"message": "No remediation actions required"}

        # Group by command for bulk execution
        grouped_actions = {}
        for action in remediation_actions:
            command_id = action["command_id"]
            if command_id not in grouped_actions:
                grouped_actions[command_id] = []
            grouped_actions[command_id].append(action)

        remediation_results = {"successful": 0, "failed": 0, "details": []}

        for command_id, actions in grouped_actions.items():
            executions = [
                {
                    "command_id": command_id,
                    "device_id": action["device_id"],
                    "username": "remediation",
                    "password": "secure-password",
                    "variables": self.build_remediation_variables(action)
                }
                for action in actions
            ]

            response = requests.post(
                f"{self.base_url}/commands/bulk-execute/",
                json={"executions": executions},
                headers=self.headers
            )

            for result in response.json()["results"]:
                if result["success"]:
                    remediation_results["successful"] += 1
                else:
                    remediation_results["failed"] += 1

                remediation_results["details"].append(result)

        return remediation_results

# Usage example
if __name__ == "__main__":
    compliance = NetworkComplianceFramework(
        netbox_url="https://netbox.example.com",
        api_token="your-api-token"
    )

    # Run compliance check on all core switches
    results = compliance.run_compliance_suite("core-switches")

    print(f"Compliance Summary:")
    print(f"- Compliant devices: {results['summary']['compliant']}")
    print(f"- Non-compliant devices: {results['summary']['non_compliant']}")

    # Execute remediation if needed
    if results["remediation_actions"]:
        print(f"\nExecuting {len(results['remediation_actions'])} remediation actions...")
        remediation_results = compliance.execute_remediation(results["remediation_actions"])
        print(f"Remediation complete: {remediation_results['successful']} successful, {remediation_results['failed']} failed")
```

**Advanced Benefits**:
- **Automated Compliance**: Complete end-to-end compliance checking
- **Bulk Operations**: Efficient execution across large device groups
- **Remediation Automation**: Automatic fixing of common issues
- **Audit Trail**: Complete logging of all compliance activities
- **Integration Ready**: Plugs into existing compliance frameworks
- **Scalability**: Handles enterprise-scale network infrastructures

## Choosing the Right Approach

### Use Web Interface When:
- **Interactive Testing**: Developing and testing new commands
- **One-off Operations**: Quick troubleshooting or configuration checks
- **Learning**: Understanding device responses and command behavior
- **Visual Analysis**: Need to see parsed data in tables and charts

### Use API When:
- **Automation**: Any repetitive or scheduled operations
- **Bulk Operations**: Multi-device command execution
- **Integration**: Connecting with other systems and tools
- **Analytics**: Advanced reporting and operational insights
- **CI/CD**: Configuration deployment pipelines
- **Compliance**: Automated compliance checking and remediation

## Best Practices

### Security
- Use dedicated service accounts for API automation
- Implement proper credential management (avoid hardcoded passwords)
- Follow principle of least privilege for permissions
- Audit API usage through command logs

### Performance
- Use bulk operations for multi-device scenarios
- Implement proper error handling and retry logic
- Monitor rate limits and execution patterns
- Cache command IDs and device mappings

### Maintenance
- Document custom commands and their business purposes
- Implement version control for automation scripts
- Monitor command success rates and update as needed
- Regular review of compliance rules and remediation procedures

This workflow documentation provides practical, real-world examples that teams can adapt to their specific environments and use cases.