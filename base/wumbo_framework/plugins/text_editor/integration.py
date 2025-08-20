"""
integration.py

This module provides integration logic for the Wumbo text editor plugin.
It enables dynamic discovery and registration of other plugins (such as
algorithm wizard, data structure wizard, LSP, etc.) with the text editor,
so their commands and features are natively available within the editor.


"""

import importlib
import pkgutil
from typing import TYPE_CHECKING, Any, Callable, Dict, List

if TYPE_CHECKING:
    from .editor_core import TextEditor

PLUGIN_PACKAGE = "wumbo_framework.plugins"

def discover_plugins() -> List[str]:
    """
    Discover available plugin submodules in the plugins package.

    Returns:
        List[str]: List of plugin submodule names (excluding 'text_editor').
    """
    import wumbo_framework.plugins
    plugin_names = []
    for finder, name, ispkg in pkgutil.iter_modules(wumbo_framework.plugins.__path__):
        if name != "text_editor":
            plugin_names.append(name)
    return plugin_names

def import_plugin_module(plugin_name: str) -> Any:
    """
    Import a plugin module by name.

    Args:
        plugin_name (str): The name of the plugin submodule.

    Returns:
        module: The imported plugin module.
    """
    full_module_name = f"{PLUGIN_PACKAGE}.{plugin_name}"
    return importlib.import_module(full_module_name)

def register_plugin_commands(editor: "TextEditor", plugin_name: str) -> None:
    """
    Register commands from a plugin with the text editor, if the plugin exposes
    a 'register_with_editor' function.

    Args:
        editor (TextEditor): The text editor instance.
        plugin_name (str): The name of the plugin submodule.
    """
    try:
        plugin_module = import_plugin_module(plugin_name)
        if hasattr(plugin_module, "register_with_editor"):
            plugin_module.register_with_editor(editor)
    except Exception as e:
        print(f"[integration] Failed to register plugin '{plugin_name}': {e}")

def auto_register_all_plugins(editor: "TextEditor") -> None:
    """
    Discover and register all available plugins with the text editor.

    Args:
        editor (TextEditor): The text editor instance.
    """
    plugin_names = discover_plugins()
    for name in plugin_names:
        register_plugin_commands(editor, name)

# Example usage (for demonstration/testing)
if __name__ == "__main__":
    from .editor_core import TextEditor

    editor = TextEditor()
    print("[integration] Discovering and registering plugins...")
    auto_register_all_plugins(editor)
    print(f"[integration] Registered commands: {list(editor.commands.keys())}")
