# MCP Plugin Marketplace

The **MCP Plugin Marketplace** is a simple command–line interface (CLI)
for browsing, installing, testing and removing plugins for Multi‑Chain
Programming (MCP) agents.  It acts like a lightweight extension
store, inspired by VS Code’s extensions gallery, and can be used to
manage local agent tools.

## Why a plugin marketplace?

Extending a product through add‑ons is a well‑established practice, and
offering those plugins through a marketplace lets users add features
on demand【253161270797461†L20-L24】.  But there are important design
choices to make when creating a marketplace: whether it lists only
in‑house add‑ons or accepts community submissions, how plugins will
integrate with the core product, and how you will manage
compatibility【253161270797461†L20-L27】.  You should also decide if you
will build your own marketplace or rely on an existing one.  Using an
existing marketplace offers exposure and trust, but sacrifices
control over what is submitted and how it’s priced【253161270797461†L61-L67】.
Building your own marketplace gives you control, but requires more
effort and benefits from inviting community submissions to rapidly
grow the selection【253161270797461†L68-L72】.

Finally, the marketplace experience must be open and easy to use for
both developers and customers: submission and review processes should
be straightforward, navigation should be intuitive, and categories
should be well organised【253161270797461†L121-L134】.  Adding ratings and
reviews gives social proof and helps users make informed decisions.

## Features

* **List available plugins** – Displays a catalogue of plugins with
  their names, versions and descriptions.
* **Install plugins** – Installs a plugin from a local package file
  into the agent’s `plugins/` directory.  Installation simply copies
  the plugin folder to the local environment.
* **Uninstall plugins** – Removes a plugin and its files.
* **Test plugins** – Runs a plugin’s built‑in test function (if
  provided) to verify it works correctly.
* **Search plugins** – Filter plugins by keyword.

## Installation

1. Clone this repository and optionally create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Use the CLI to manage your MCP plugins.  The following commands are
available:

```bash
# List available (remote) plugins
python -m mcp_plugin_marketplace.cli list

# Install a plugin from a local zip file
python -m mcp_plugin_marketplace.cli install path/to/plugin.zip

# Uninstall a plugin by name
python -m mcp_plugin_marketplace.cli uninstall plugin_name

# Test a plugin
python -m mcp_plugin_marketplace.cli test plugin_name
```

Plugins must implement a simple interface: they should be Python
packages with a `manifest.json` file describing the plugin (name,
version, description) and a `plugin.py` module exposing a
`run_test()` function used by the marketplace’s `test` command.  See
the `sample_plugin` directory for an example.

## How it works

Plugins are stored in a directory called `plugins_installed/` in your
home directory.  The marketplace reads plugin metadata from
`manifest.json` files, allowing it to list installed plugins.  It also
loads a catalogue of available plugins from a JSON file (you can
configure the source).  Installing a plugin copies the plugin folder
into your local environment; uninstalling removes it.

The CLI is built with `click` and uses standard Python file operations.
It does **not** download plugins from remote servers by default;
instead it expects you to provide a local archive.  In future
versions, you could implement remote downloads and authentication.

## Limitations and future work

This marketplace provides a basic scaffold and does not handle
versioning conflicts, dependencies between plugins, or update
notifications.  It does not sign plugins or verify signatures.  The
plugin testing system only calls a single `run_test()` function and
assumes the plugin is safe to execute.  To make this tool production
ready you should implement security checks, version and dependency
management, remote catalogue integration, and a web UI.

## References

* **Add‑on marketplaces** – Offering plugins through a marketplace lets
  users add features only when needed, but it requires decisions
  about scope (in‑house vs community) and compatibility management【253161270797461†L20-L27】.
* **Marketplace design choices** – Building your own marketplace gives
  control but requires more effort; using an existing marketplace
  provides exposure but less control【253161270797461†L61-L67】.  Opening the
  marketplace to community submissions can rapidly expand your
  catalogue【253161270797461†L68-L72】.
* **User experience** – A marketplace should be visible and easy to
  navigate for both developers and customers, with a simple
  submission process and intuitive search【253161270797461†L121-L134】.