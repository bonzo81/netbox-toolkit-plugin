from netbox.choices import ButtonColorChoices
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem

menu = PluginMenu(
    label="Command Toolkit",
    icon_class="mdi mdi-console",
    groups=(
        (
            "Commands",
            (
                PluginMenuItem(
                    link="plugins:netbox_toolkit_plugin:command_list",
                    link_text="Commands",
                    permissions=["netbox_toolkit_plugin.view_command"],
                    buttons=(
                        PluginMenuButton(
                            "plugins:netbox_toolkit_plugin:command_add",
                            "Add",
                            "mdi mdi-plus-thick",
                            ButtonColorChoices.GRAY,
                            permissions=["netbox_toolkit_plugin.add_command"],
                        ),
                    ),
                ),
                PluginMenuItem(
                    link="plugins:netbox_toolkit_plugin:commandlog_list",
                    link_text="Command Logs",
                    permissions=["netbox_toolkit_plugin.view_commandlog"],
                ),
                PluginMenuItem(
                    link="plugins:netbox_toolkit_plugin:toolkit_stats",
                    link_text="Statistics",
                    permissions=["netbox_toolkit_plugin.view_commandlog"],
                ),
            ),
        ),
        (
            "Credentials",
            (
                PluginMenuItem(
                    link="plugins:netbox_toolkit_plugin:devicecredentialset_list",
                    link_text="Device Credentials",
                    permissions=["netbox_toolkit_plugin.view_devicecredentialset"],
                    buttons=(
                        PluginMenuButton(
                            "plugins:netbox_toolkit_plugin:devicecredentialset_add",
                            "Add",
                            "mdi mdi-plus-thick",
                            ButtonColorChoices.GRAY,
                            permissions=[
                                "netbox_toolkit_plugin.add_devicecredentialset"
                            ],
                        ),
                    ),
                ),
            ),
        ),
    ),
)
