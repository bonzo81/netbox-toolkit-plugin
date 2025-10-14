# API vs Web Interface Feature Comparison

This document provides a comprehensive comparison between the NetBox Toolkit Plugin's REST API and Web Interface capabilities.


## Detailed Comparison

### Permission Creation & Management

| Capability | Web Interface | API | Notes |
|-----------|---------------|-----|-------|
| **Create ObjectPermissions** | ✅ NetBox UI | ✅ NetBox API | Uses NetBox's built-in permission system |
| **Assign Actions** | ✅ `execute_show`, `execute_config` | ✅ Same actions | Custom permission actions |
| **User/Group Assignment** | ✅ Visual selection | ✅ Programmatic assignment | - |
| **Bulk Permission Creation** | ❌ Manual only | ✅ API automation | API enables programmatic permission management |
| **Permission Templates** | ❌ | ✅ Scriptable | Create standardized permission sets via API |
| **Constraint Configuration** | ✅ Visual form | ✅ JSON structure | API requires understanding of constraint syntax |

---

### Credential Creation & Management

| Capability | Web Interface | API | Notes |
|-----------|---------------|-----|-------|
| **Create Credential Sets** | ✅ Form-based | ❌ | **Web Interface only** - Security by design |
| **Edit/Update Credentials** | ✅ Edit form | ❌ | **Web Interface only** - Prevents password transmission |
| **Delete Credential Sets** | ✅ Delete action | ❌ | **Web Interface only** |
| **Platform Restrictions** | ✅ Multi-select platforms | ❌ | Configure during web creation |
| **Generate Access Token** | ✅ Auto-generated on save | N/A | Token used for API command execution |
| **View Token** | ✅ Displayed after creation | N/A | Token visible only once for security |
| **View Credential List** | ✅ List view | ❌ | **Web Interface only** |
| **Credential Encryption** | ✅ Automatic | N/A | Passwords encrypted at rest |
| **Last Used Tracking** | ✅ Displayed in list | N/A | Automatic timestamp updates |
| **Active/Inactive Status** | ✅ Toggle switch | N/A | Disable without deletion |
| **Use Token in Execution** | N/A | ✅ `credential_token` field | API uses tokens, not credentials directly |

**Use Web Interface For:**

- **ALL credential management operations** (create, edit, delete)

**API Design:**

- ❌ **No API endpoints for credential CRUD** - By design for security
- ✅ **API uses credential tokens only** - Created via Web Interface
- 🔒 **Why?** Prevents password transmission over API, enforces secure credential management

**Security Note:** Credentials (username/password) can only be created and managed through the Web Interface. The API accepts only pre-generated `credential_token` values for command execution, ensuring passwords are never transmitted via API calls.

---

### Command Creation

| Capability | Web Interface | API | Notes |
|-----------|---------------|-----|-------|
| **Create/Edit Commands** | ✅ Form-based | ✅ Programmatic | Full CRUD operations |
| **Variable Management** | ✅ Inline formsets | ✅ Nested serializers | Create variables with commands |
| **Platform Assignment** | ✅ Multi-select dropdown | ✅ Array of IDs | Assign multiple platforms |
| **Command Type Selection** | ✅ Radio buttons | ✅ String field | `show` or `config` |
| **Validation** | ✅ Real-time form validation | ✅ Serializer validation | Same validation rules |
| **Advanced Filtering** | ⚠️ Basic search | ✅ Full filter options | API: filter by platform, type, name patterns |
| **Bulk Command Creation** | ❌ | ✅ API automation | Create multiple commands programmatically |
| **Import from Templates** | ❌ | ✅ Scriptable | Import command libraries via API |

---

### Command Execution

| Capability | Web Interface | API | Notes |
|-----------|---------------|-----|-------|
| **Single Device Execution** | ✅ Interactive form | ✅ POST `/execute/` | Same functionality |
| **Multi-Device Execution** | ❌ | ✅ POST `/bulk-execute/` | **API exclusive** |
| **Variable Discovery** | ✅ Dynamic dropdowns | ✅ GET `/variable-choices/` | API enables programmatic discovery |
| **Variable Validation** | ✅ Client-side validation | ✅ Enhanced server validation | API provides detailed error messages |
| **Real-time Output** | ✅ Live display | ✅ JSON response | Web shows formatted, API returns structured |
| **Syntax Error Detection** | ✅ Visual indicators | ✅ Response field | Both detect and report syntax errors |
| **Parsed Output** | ✅ Download CSV | ✅ JSON field | API includes parsed data in response |
| **Credential Management** | ✅ Credential Set selection | ✅ `credential_token` | Both use DeviceCredentialSet tokens |
| **Rate Limit Status** | ✅ Real-time widget | ⚠️ Check separately | Web shows live status |
| **Execution Timeout** | ✅ Default 30s | ✅ Configurable 5-300s | API allows custom timeout |

---

### Command History & Logging

| Capability | Web Interface | API | Notes |
|-----------|---------------|-----|-------|
| **Browse History** | ✅ Paginated list | ✅ GET `/command-logs/` | Both support filtering |
| **View Execution Details** | ✅ Detail page | ✅ GET `/command-logs/{id}/` | Full execution details |
| **Filter by Device** | ✅ Filter form | ✅ `?device_id=` | - |
| **Filter by Command** | ✅ Filter form | ✅ `?command_id=` | - |
| **Filter by User** | ✅ Filter form | ✅ `?user_id=` | - |
| **Filter by Date Range** | ✅ Date picker | ✅ `?created__gte=&created__lte=` | API supports more date formats |
| **Filter by Success/Failure** | ✅ Status filter | ✅ `?success=true/false` | - |
| **Export Single Log CSV** | ✅ Per-log download | ✅ Included in response | Export parsed data |
| **Bulk Export** | ❌ | ✅ GET `/export/?format=csv` | **API exclusive** |
| **Date-Filtered Export** | ❌ | ✅ `&start_date=&end_date=` | **API exclusive** |
| **Statistics Dashboard** | ✅ Statistics page | ✅ GET `/statistics/` | Both show same metrics |
| **Success Rate Analytics** | ✅ Visual charts | ✅ JSON response | Same data, different format |
| **Error Pattern Analysis** | ✅ Common errors table | ✅ Common errors report | Same data, different format |
| **Top Commands Report** | ✅ Visual ranking | ✅ Statistics endpoint | Same data, different format |
| **Recent Activity Widget** | ✅ Last 24h stats | ✅ Statistics endpoint | Web shows widget, API returns data |

---

## API-Exclusive Use Cases

The following capabilities are **only available** through the API and have no Web Interface equivalent:

### 1. Bulk Multi-Device Execution
```bash
# Execute command across multiple devices simultaneously
curl -X POST "https://netbox.example.com/api/plugins/toolkit/commands/bulk-execute/" \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "executions": [
      {
        "command_id": 5,
        "device_id": 101,
        "credential_token": "YOUR_CREDENTIAL_TOKEN",
        "variables": {"vlan_id": "100", "description": "Guest Network"}
      },
      {
        "command_id": 5,
        "device_id": 102,
        "credential_token": "YOUR_CREDENTIAL_TOKEN",
        "variables": {"vlan_id": "100", "description": "Guest Network"}
      }
    ]
  }'
```

### 2. Bulk Export with Date Filtering
```bash
# Export filtered logs for compliance reporting
GET /api/plugins/toolkit/command-logs/export/?format=csv&start_date=2025-01-01&end_date=2025-12-31
```

### 3. Programmatic Variable Discovery
```bash
# Discover available variable choices for a device
GET /api/plugins/toolkit/commands/1/variable-choices/?device_id=123

# Returns NetBox data (interfaces, VLANs, IPs) available for that device
```

### 4. Programmatic Statistics Access
```bash
# Get execution statistics in JSON format for integration with monitoring systems
GET /api/plugins/toolkit/command-logs/statistics/

# Response includes:
# - Overall success rate
# - Last 24h execution counts
# - Top 10 most-used commands
# - Common error patterns
```

**Note:** While statistics are viewable in both the Web Interface (visual dashboard) and API (JSON response), the API format is designed for programmatic integration with external monitoring and reporting systems.

---

## Conclusion

The NetBox Toolkit Plugin provides **complete feature parity** between its web interface and API for core functionality, with the API offering **additional capabilities** for automation, integration, and programmatic workflows. Users can seamlessly transition between both interfaces based on their specific use cases.

**Key Distinctions:**

- **Credential Management**: **Web Interface only** - All credential CRUD operations must be done via web for security
- **Statistics & Analytics**: Available in both—Web Interface provides visual dashboards, API provides JSON for programmatic integration
- **Bulk Operations**: API-exclusive for multi-device command execution
- **Export**: Web Interface supports single-log CSV export, API supports bulk export with date filtering
- **Command Execution**: Single device in Web Interface, single or bulk in API

