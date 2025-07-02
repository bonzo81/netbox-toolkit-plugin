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
                    link="plugins:netbox_toolkit:command_list",
                    link_text="Commands",
                    buttons=(
                        PluginMenuButton(
                            "plugins:netbox_toolkit:command_add",
                            "Add",
                            "mdi mdi-plus-thick",
                            ButtonColorChoices.GRAY
                        ),
                    )
                ),
                PluginMenuItem(
                    link="plugins:netbox_toolkit:commandlog_list",
                    link_text="Command Logs",
                ),
            ),
        ),
    ),
)