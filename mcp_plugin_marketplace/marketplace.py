"""Core marketplace logic for MCP Plugin Marketplace."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


@dataclass
class PluginMetadata:
    """Metadata describing a plugin."""

    name: str
    version: str
    description: str
    path: Path  # installed path


class Marketplace:
    """Simple plugin marketplace manager."""

    def __init__(
        self,
        catalogue_path: Optional[str] = None,
        install_dir: Optional[str | Path] = None,
    ) -> None:
        """Initialise the marketplace.

        Parameters
        ----------
        catalogue_path : str, optional
            Path to a JSON file describing available plugins.  If
            omitted, a bundled ``available_plugins.json`` file is used.
        install_dir : str or Path, optional
            Directory where plugins will be installed.  Defaults to
            ``~/.mcp/plugins_installed``.
        """
        if install_dir is None:
            home = Path.home()
            install_dir = home / ".mcp" / "plugins_installed"
        self.install_dir: Path = Path(install_dir)
        self.install_dir.mkdir(parents=True, exist_ok=True)
        # Determine catalogue file
        if catalogue_path is None:
            # Use file relative to this module
            self.catalogue_path = Path(__file__).resolve().parent / "available_plugins.json"
        else:
            self.catalogue_path = Path(catalogue_path)
        self.catalogue: List[Dict[str, str]] = []
        self._load_catalogue()

    def _load_catalogue(self) -> None:
        """Load available plugins from the JSON catalogue."""
        if not self.catalogue_path.exists():
            self.catalogue = []
            return
        with open(self.catalogue_path, "r", encoding="utf-8") as fh:
            try:
                self.catalogue = json.load(fh)
            except json.JSONDecodeError:
                self.catalogue = []

    def list_available(self) -> List[Dict[str, str]]:
        """Return the list of available plugins from the catalogue."""
        return self.catalogue

    def list_installed(self) -> List[PluginMetadata]:
        """Return a list of installed plugins with metadata."""
        plugins: List[PluginMetadata] = []
        if not self.install_dir.exists():
            return plugins
        for sub in self.install_dir.iterdir():
            if sub.is_dir():
                manifest = sub / "manifest.json"
                if manifest.exists():
                    try:
                        with open(manifest, "r", encoding="utf-8") as fh:
                            meta = json.load(fh)
                        plugins.append(
                            PluginMetadata(
                                name=meta.get("name", sub.name),
                                version=meta.get("version", "0.0.0"),
                                description=meta.get("description", ""),
                                path=sub,
                            )
                        )
                    except Exception:
                        continue
        return plugins

    def install(self, plugin_source: str) -> PluginMetadata:
        """Install a plugin from a local directory or zip file.

        Returns metadata for the installed plugin.
        """
        src = Path(plugin_source)
        if not src.exists():
            raise FileNotFoundError(f"Plugin source not found: {plugin_source}")
        if src.suffix.lower() == ".zip":
            # Extract zip to a temporary folder then move
            import zipfile
            with zipfile.ZipFile(src, "r") as z:
                tmpdir = Path(self.install_dir) / (src.stem + "_tmp")
                tmpdir.mkdir(parents=True, exist_ok=True)
                z.extractall(tmpdir)
                # plugin root should contain manifest.json
                # move the first level if nested
                candidates = [p for p in tmpdir.iterdir() if p.is_dir()]
                if len(candidates) == 1:
                    extracted_root = candidates[0]
                else:
                    extracted_root = tmpdir
                dest = self.install_dir / extracted_root.name
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.move(str(extracted_root), dest)
                shutil.rmtree(tmpdir, ignore_errors=True)
                installed_path = dest
        elif src.is_dir():
            dest = self.install_dir / src.name
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(src, dest)
            installed_path = dest
        else:
            raise ValueError("Plugin source must be a directory or zip file")
        # Read manifest
        manifest_file = installed_path / "manifest.json"
        if not manifest_file.exists():
            raise ValueError("Invalid plugin: missing manifest.json")
        with open(manifest_file, "r", encoding="utf-8") as fh:
            meta = json.load(fh)
        return PluginMetadata(
            name=meta.get("name", installed_path.name),
            version=meta.get("version", "0.0.0"),
            description=meta.get("description", ""),
            path=installed_path,
        )

    def uninstall(self, plugin_name: str) -> bool:
        """Uninstall a plugin by name.  Returns True if removed."""
        dest = self.install_dir / plugin_name
        if dest.exists() and dest.is_dir():
            shutil.rmtree(dest)
            return True
        return False

    def test(self, plugin_name: str) -> bool:
        """Run the plugin's test function.  Returns True if test passes."""
        plugin_dir = self.install_dir / plugin_name
        if not plugin_dir.exists():
            raise ValueError(f"Plugin '{plugin_name}' not installed")
        # Expect plugin.py with run_test function
        plugin_module_file = plugin_dir / "plugin.py"
        if not plugin_module_file.exists():
            raise ValueError(f"Plugin '{plugin_name}' has no plugin.py")
        # Add plugin_dir to sys.path temporarily
        sys.path.insert(0, str(plugin_dir))
        try:
            spec = importlib.util.spec_from_file_location(
                f"{plugin_name}_module", plugin_module_file
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)  # type: ignore[call-arg]
            else:
                raise ImportError("Could not load plugin module")
            if not hasattr(module, "run_test"):
                raise AttributeError("Plugin does not define run_test()")
            result = module.run_test()
            return bool(result)
        finally:
            # Remove path entry
            sys.path = [p for p in sys.path if p != str(plugin_dir)]