# Text Editor Plugin for Wumbo

The **Text Editor Plugin** provides a modular, extensible text editing environment within the Wumbo framework. It is designed to natively support and integrate with other Wumbo plugins, such as the Algorithm Wizard, Data Structure Wizard, and LSP (Language Server Protocol) integration, enabling seamless workflows for code editing, prototyping, and code intelligence.

---

## Features

- **Basic Text Editing:** Open, edit, and save files or text buffers.
- **Plugin Command Registration:** Dynamically discover and register commands from other plugins (e.g., run an algorithm, insert a data structure).
- **LSP Integration:** Support for code completion, go-to-definition, hover, and diagnostics via the LSP plugin.
- **Extensible UI:** Designed for CLI, TUI, or web-based frontends.

---

## Directory Structure

```
text_editor/
├── README.md           # This file
├── __init__.py         # Package initializer
├── editor_core.py      # Main text editor logic and API
├── integration.py      # Plugin discovery and integration logic
```

---

## Usage

### 1. Basic Editor Operations

The core editor class provides methods to open, edit, and save files:

```python
from wumbo_framework.plugins.text_editor.editor_core import TextEditor

editor = TextEditor()
editor.open_file("example.py")
editor.buffers["example.py"] += "\n# New line"
editor.save_file("example.py")
```

### 2. Registering Plugin Commands

Plugins can register commands with the editor, making their functionality available as editor actions:

```python
def run_algorithm_wizard(*args, **kwargs):
    # Call the algorithm wizard plugin here
    pass

editor.register_command("run_algorithm_wizard", run_algorithm_wizard)
editor.run_command("run_algorithm_wizard", arg1, arg2)
```

### 3. LSP Integration

The editor can use the LSP plugin to provide code intelligence features:

```python
# Example (pseudo-code)
from wumbo_framework.plugins.lsp.lsp_function import LSPClient

lsp_client = LSPClient(["pylsp"])
editor.lsp_client = lsp_client
# Now the editor can provide completion, hover, etc.
```

---

## Extending the Editor

- **Add New Plugins:** Place your plugin in `wumbo_framework/plugins/` and expose a `register_with_editor(editor)` function.
- **UI/UX:** Implement a CLI, TUI, or web frontend that interacts with the `TextEditor` API.
- **Custom Commands:** Register custom commands for new workflows, code generation, or automation.

---

## Example Workflow

1. User opens a file in the editor.
2. User selects "Insert Data Structure" from the command palette.
3. The editor invokes the Data Structure Wizard plugin, which inserts code at the cursor.
4. User runs "Run Algorithm Wizard" to generate and execute an algorithm on selected data.
5. LSP plugin provides code completion and diagnostics as the user types.

---

## Contributing

- Follow the Wumbo plugin architecture for consistency.
- Document new commands and integration points in this README.
- See `base/docs/CONTRIBUTING.md` for general contribution guidelines.

---

## License

MIT License. Use, modify, and extend as needed.

---