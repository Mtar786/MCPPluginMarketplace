"""Sample plugin for MCP Plugin Marketplace.

This simple plugin demonstrates the expected structure of a plugin.
It defines a ``run_test`` function that the marketplace can call.
"""


def run_test() -> bool:
    """Run a basic test for the plugin.

    Returns True to indicate the plugin is functioning.
    """
    print("Hello from sample_plugin! This plugin is installed and working.")
    return True