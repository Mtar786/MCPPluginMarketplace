"""Command line interface for MCP Plugin Marketplace."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click

from .marketplace import Marketplace


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.option(
    "--catalogue",
    "catalogue_path",
    type=click.Path(exists=True, dir_okay=False, readable=True, path_type=str),
    default=None,
    help="Path to a JSON file describing available plugins.  If omitted, the default bundled catalogue is used.",
)
@click.option(
    "--install-dir",
    "install_dir",
    type=click.Path(dir_okay=True, file_okay=False, path_type=str),
    default=None,
    help="Directory where plugins are installed.  Defaults to ~/.mcp/plugins_installed.",
)
@click.pass_context
def cli(ctx: click.Context, catalogue_path: Optional[str], install_dir: Optional[str]) -> None:
    """Manage MCP plugins."""
    ctx.obj = Marketplace(catalogue_path=catalogue_path, install_dir=install_dir)


@cli.command()
@click.pass_obj
def list(obj: Marketplace) -> None:
    """List available plugins in the catalogue."""
    available = obj.list_available()
    if not available:
        click.echo("No available plugins found in the catalogue.")
        return
    click.echo("Available plugins:")
    for plugin in available:
        click.echo(f"- {plugin.get('name')} {plugin.get('version')}: {plugin.get('description')}")


@cli.command()
@click.pass_obj
def installed(obj: Marketplace) -> None:
    """List currently installed plugins."""
    installed = obj.list_installed()
    if not installed:
        click.echo("No plugins installed.")
        return
    click.echo("Installed plugins:")
    for plugin in installed:
        click.echo(f"- {plugin.name} {plugin.version}: {plugin.description}")


@cli.command()
@click.argument("source", type=click.Path(exists=True, dir_okay=True, path_type=str))
@click.pass_obj
def install(obj: Marketplace, source: str) -> None:
    """Install a plugin from a local directory or zip file."""
    plugin = obj.install(source)
    click.echo(f"Installed {plugin.name} version {plugin.version}")


@cli.command()
@click.argument("plugin_name", type=str)
@click.pass_obj
def uninstall(obj: Marketplace, plugin_name: str) -> None:
    """Uninstall a plugin by name."""
    success = obj.uninstall(plugin_name)
    if success:
        click.echo(f"Uninstalled {plugin_name}")
    else:
        click.echo(f"Plugin '{plugin_name}' not found")


@cli.command()
@click.argument("plugin_name", type=str)
@click.pass_obj
def test(obj: Marketplace, plugin_name: str) -> None:
    """Test an installed plugin by running its run_test function."""
    try:
        success = obj.test(plugin_name)
        if success:
            click.echo(f"Plugin '{plugin_name}' test passed")
        else:
            click.echo(f"Plugin '{plugin_name}' test returned False")
    except Exception as e:
        click.echo(f"Error testing plugin '{plugin_name}': {e}")


@cli.command()
@click.argument("keyword", type=str)
@click.pass_obj
def search(obj: Marketplace, keyword: str) -> None:
    """Search available plugins by keyword."""
    keyword_lower = keyword.lower()
    matches = [p for p in obj.list_available() if keyword_lower in p.get("name", "").lower() or keyword_lower in p.get("description", "").lower()]
    if not matches:
        click.echo(f"No available plugins matching '{keyword}'.")
        return
    click.echo(f"Plugins matching '{keyword}':")
    for plugin in matches:
        click.echo(f"- {plugin.get('name')} {plugin.get('version')}: {plugin.get('description')}")


if __name__ == "__main__":  # pragma: no cover
    cli()