"""
ui.py

Terminal-based UI for the Wumbo Text Editor Plugin.
---------------------------------------------------

This module provides a simple command-line interface (CLI) for interacting with the
Wumbo text editor core. It allows users to open, edit, save, and view files, as well
as list and run plugin commands, all from an interactive shell.

Features:
- Open, edit, save, and view files/buffers
- List and run registered plugin commands
- Switch between open buffers
- Extensible for future TUI or GUI frontends


"""

import cmd
import os
from typing import Optional

from .editor_core import TextEditor
from .integration import auto_register_all_plugins

class TextEditorShell(cmd.Cmd):
    intro = "Welcome to the Wumbo Text Editor shell. Type help or ? to list commands.\n"
    prompt = "(wumbo-editor) "

    def __init__(self):
        super().__init__()
        self.editor = TextEditor()
        auto_register_all_plugins(self.editor)

    def do_open(self, arg):
        "Open a file: open <filename>"
        filename = arg.strip()
        if not filename:
            print("Usage: open <filename>")
            return
        try:
            self.editor.open_file(filename)
            print(f"Opened file: {filename}")
        except Exception as e:
            print(f"Error opening file: {e}")

    def do_save(self, arg):
        "Save the current file or a specified file: save [<filename>]"
        filename = arg.strip() or None
        try:
            self.editor.save_file(filename)
            print(f"File saved: {filename or self.editor.current_file}")
        except Exception as e:
            print(f"Error saving file: {e}")

    def do_edit(self, arg):
        "Edit the current file or a specified file: edit [<filename>]"
        filename = arg.strip() or self.editor.current_file
        if not filename:
            print("No file specified or open.")
            return
        if filename not in self.editor.buffers:
            print(f"File '{filename}' is not open. Use 'open <filename>' first.")
            return
        print("Enter new content. End with a single '.' on a line by itself.")
        lines = []
        while True:
            line = input()
            if line.strip() == ".":
                break
            lines.append(line)
        new_content = "\n".join(lines)
        self.editor.edit_buffer(new_content, filename)
        print(f"Buffer for '{filename}' updated.")

    def do_view(self, arg):
        "View the contents of the current file or a specified file: view [<filename>]"
        filename = arg.strip() or self.editor.current_file
        if not filename or filename not in self.editor.buffers:
            print("No file specified or open.")
            return
        print(f"--- {filename} ---")
        print(self.editor.get_buffer(filename))
        print(f"--- End of {filename} ---")

    def do_buffers(self, arg):
        "List all open buffers."
        if not self.editor.buffers:
            print("No open buffers.")
            return
        print("Open buffers:")
        for fname in self.editor.buffers:
            marker = "*" if fname == self.editor.current_file else " "
            print(f"{marker} {fname}")

    def do_switch(self, arg):
        "Switch to another open buffer: switch <filename>"
        filename = arg.strip()
        if not filename:
            print("Usage: switch <filename>")
            return
        if filename not in self.editor.buffers:
            print(f"Buffer '{filename}' is not open.")
            return
        self.editor.current_file = filename
        print(f"Switched to buffer: {filename}")

    def do_list(self, arg):
        "List all registered plugin/editor commands."
        commands = self.editor.list_commands()
        if not commands:
            print("No commands registered.")
            return
        print("Registered commands:")
        for cmd_name in commands:
            print(f"- {cmd_name}")

    def do_run(self, arg):
        "Run a registered command: run <command_name> [args]"
        parts = arg.strip().split()
        if not parts:
            print("Usage: run <command_name> [args]")
            return
        cmd_name = parts[0]
        cmd_args = parts[1:]
        try:
            result = self.editor.run_command(cmd_name, *cmd_args)
            if result is not None:
                print(f"Result: {result}")
        except Exception as e:
            print(f"Error running command '{cmd_name}': {e}")

    def do_exit(self, arg):
        "Exit the editor shell."
        print("Exiting Wumbo Text Editor shell.")
        return True

    def do_quit(self, arg):
        "Exit the editor shell."
        return self.do_exit(arg)

    def do_EOF(self, arg):
        "Exit the editor shell (Ctrl-D)."
        print()
        return self.do_exit(arg)

    def emptyline(self):
        pass

if __name__ == "__main__":
    TextEditorShell().cmdloop()
