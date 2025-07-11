#!/usr/bin/env python3
"""
Test script to verify the plugin configuration can be imported correctly.
"""


def test_plugin_import():
    try:
        # Test importing the plugin config
        from netbox_toolkit_plugin import config

        print("✓ Successfully imported plugin config")
        print(f"✓ Config object: {config}")
        print(f"✓ Config name: {config.name}")
        print(f"✓ Config verbose_name: {config.verbose_name}")
        return True
    except Exception as e:
        print(f"✗ Error importing plugin config: {e}")
        return False


def test_toolkitsettings_import():
    try:
        # Test importing the ToolkitSettings class
        from netbox_toolkit_plugin.config import ToolkitSettings

        print("✓ Successfully imported ToolkitSettings")
        print(f"✓ ToolkitSettings class: {ToolkitSettings}")
        return True
    except Exception as e:
        print(f"✗ Error importing ToolkitSettings: {e}")
        return False


if __name__ == "__main__":
    print("Testing NetBox Toolkit Plugin Configuration...")
    print("=" * 50)

    success1 = test_plugin_import()
    print()
    success2 = test_toolkitsettings_import()

    print("\n" + "=" * 50)
    if success1 and success2:
        print("✓ All tests passed! Plugin configuration is working correctly.")
    else:
        print("✗ Some tests failed. Please check the errors above.")
