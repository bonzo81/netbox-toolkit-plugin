# Platform Support

The plugin uses **Scrapli** as the primary connection library with **Netmiko** as a fallback, providing robust support for various network device platforms.

## Primary Connection Engine: Scrapli

Scrapli provides fast, modern SSH connectivity with structured output parsing capabilities:

- **Cisco IOS/IOS-XE** (`cisco_ios`)
- **Cisco NX-OS** (`cisco_nxos`)
- **Cisco IOS-XR** (`cisco_iosxr`)
- **Juniper Junos** (`juniper_junos`)
- **Arista EOS** (`arista_eos`)

## Fallback Connection: Netmiko

When Scrapli encounters connection issues, the plugin automatically falls back to Netmiko for broader device compatibility:

- **Extended Platform Support** - Covers additional vendor platforms and older device models
- **Legacy Device Support** - Better compatibility with older firmware versions
- **SSH Troubleshooting** - Alternative SSH implementation for problematic connections

## Key Benefits

- **Automatic Fallback**: Seamless switching between connection methods
- **TextFSM Integration**: Structured data parsing for show commands
- **JSON Output**: Native support for modern network OS JSON responses

## Platform Configuration

Platforms are configured in NetBox's DCIM section. The plugin uses the platform's `slug` field to determine the appropriate connector:

- Ensure your devices have the correct platform assigned
- Use standard platform slugs (e.g., `cisco_ios`, `cisco_nxos`, `juniper_junos`)
- The plugin automatically normalizes platform names for compatibility

For detailed configuration, see the [Plugin Configuration Guide](./user/plugin-configuration.md).
