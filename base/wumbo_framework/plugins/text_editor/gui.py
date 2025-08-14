Wumbo/base/wumbo_framework/plugins/text_editor/gui.py
"""
gui.py

A basic GUI interface for the Wumbo Text Editor Plugin using tkinter.
This module provides a simple graphical text editor window that can be
launched from the TUI or directly as a standalone script.

Features:
- Open, edit, and save files in a text area
- List and switch between open buffers
- Run registered plugin/editor commands from a menu
- Designed to be extensible for future enhancements


"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from typing import Optional

from .editor_core import TextEditor

class WumboTextEditorGUI:
    def __init__(self, editor: Optional[TextEditor] = None):
        self.editor = editor or TextEditor()
        self.root = tk.Tk()
        self.root.title("Wumbo Text Editor")
        self.text_area = tk.Text(self.root, wrap=tk.NONE, undo=True)
        self.text_area.pack(fill=tk.BOTH, expand=1)
        self.current_file = None

        # Menu
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)
        self._build_file_menu()
        self._build_command_menu()
        self._build_buffer_menu()

        # Status bar
        self.status = tk.StringVar()
        self.status.set("Ready")
        self.status_bar = tk.Label(self.root, textvariable=self.status, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_file_menu(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Open...", command=self.open_file)
        file_menu.add_command(label="Save", command=self.save_file)
        file_menu.add_command(label="Save As...", command=self.save_file_as)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

    def _build_command_menu(self):
        command_menu = tk.Menu(self.menu, tearoff=0)
        command_menu.add_command(label="List Commands", command=self.list_commands)
        command_menu.add_command(label="Run Command...", command=self.run_command_prompt)
        self.menu.add_cascade(label="Commands", menu=command_menu)

    def _build_buffer_menu(self):
        buffer_menu = tk.Menu(self.menu, tearoff=0)
        buffer_menu.add_command(label="List Buffers", command=self.list_buffers)
        buffer_menu.add_command(label="Switch Buffer...", command=self.switch_buffer_prompt)
        self.menu.add_cascade(label="Buffers", menu=buffer_menu)

    def open_file(self):
        filename = filedialog.askopenfilename()
        if filename:
            try:
                self.editor.open_file(filename)
                self.current_file = filename
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(tk.END, self.editor.get_buffer(filename))
                self.status.set(f"Opened: {filename}")
            except Exception as e:
                messagebox.showerror("Open File", f"Error: {e}")

    def save_file(self):
        if not self.current_file:
            self.save_file_as()
            return
        try:
            content = self.text_area.get(1.0, tk.END)
            self.editor.edit_buffer(content, self.current_file)
            self.editor.save_file(self.current_file)
            self.status.set(f"Saved: {self.current_file}")
        except Exception as e:
            messagebox.showerror("Save File", f"Error: {e}")

    def save_file_as(self):
        filename = filedialog.asksaveasfilename()
        if filename:
            try:
                content = self.text_area.get(1.0, tk.END)
                self.editor.edit_buffer(content, filename)
                self.editor.save_file(filename)
                self.current_file = filename
                self.status.set(f"Saved As: {filename}")
            except Exception as e:
                messagebox.showerror("Save File As", f"Error: {e}")

    def list_commands(self):
        commands = self.editor.list_commands()
        if not commands:
            messagebox.showinfo("Commands", "No commands registered.")
        else:
            messagebox.showinfo("Commands", "\n".join(commands))

    def run_command_prompt(self):
        commands = self.editor.list_commands()
        if not commands:
            messagebox.showinfo("Run Command", "No commands registered.")
            return
        cmd_name = simpledialog.askstring("Run Command", f"Enter command name:\nAvailable: {', '.join(commands)}")
        if cmd_name and cmd_name in commands:
            try:
                result = self.editor.run_command(cmd_name)
                messagebox.showinfo("Command Result", str(result))
            except Exception as e:
                messagebox.showerror("Run Command", f"Error: {e}")
        elif cmd_name:
            messagebox.showwarning("Run Command", f"Command '{cmd_name}' not found.")

    def list_buffers(self):
        buffers = list(self.editor.buffers.keys())
        if not buffers:
            messagebox.showinfo("Buffers", "No open buffers.")
        else:
            current = self.current_file or "(none)"
            msg = "\n".join([f"{'*' if fname == current else ' '} {fname}" for fname in buffers])
            messagebox.showinfo("Buffers", msg)

    def switch_buffer_prompt(self):
        buffers = list(self.editor.buffers.keys())
        if not buffers:
            messagebox.showinfo("Switch Buffer", "No open buffers.")
            return
        fname = simpledialog.askstring("Switch Buffer", f"Enter buffer filename:\nAvailable: {', '.join(buffers)}")
        if fname and fname in buffers:
            self.current_file = fname
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, self.editor.get_buffer(fname))
            self.status.set(f"Switched to buffer: {fname}")
        elif fname:
            messagebox.showwarning("Switch Buffer", f"Buffer '{fname}' not found.")

    def run(self):
        self.root.mainloop()

# Launcher function for use from TUI or other modules
def launch_gui(editor: Optional[TextEditor] = None):
    """
    Launch the Wumbo Text Editor GUI.

    Args:
        editor (TextEditor, optional): An existing TextEditor instance to use.
    """
    gui = WumboTextEditorGUI(editor)
    gui.run()

# Allow running as a standalone script
if __name__ == "__main__":
    launch_gui()
