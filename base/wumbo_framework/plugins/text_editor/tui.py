Wumbo/base/wumbo_framework/plugins/text_editor/tui.py
"""
tui.py

Rich Terminal UI for the Wumbo Text Editor Plugin using prompt_toolkit.
-----------------------------------------------------------------------

This module provides a Text-based User Interface (TUI) for the Wumbo text editor,
featuring a main text area, buffer list, and command palette. It also includes
the ability to launch a simple GUI (Tkinter-based) from within the TUI.

Features:
- Main text editing area with basic navigation and editing
- Buffer list for switching between open files
- Command palette for running plugin/editor commands
- Launch GUI mode from the TUI

Author: [Your Name]
Date: [YYYY-MM-DD]
"""

from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout import Layout, HSplit, VSplit, Window
from prompt_toolkit.widgets import TextArea, Frame, Button, Dialog, Label, MenuContainer, MenuItem
from prompt_toolkit.shortcuts import message_dialog, input_dialog
from prompt_toolkit.styles import Style
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.margins import ScrollbarMargin
import threading

from .editor_core import TextEditor
from .integration import auto_register_all_plugins

# --- GUI Launcher (Tkinter) ---
def launch_gui(editor: TextEditor):
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext

    class WumboGUI(tk.Tk):
        def __init__(self, editor: TextEditor):
            super().__init__()
            self.editor = editor
            self.title("Wumbo Text Editor (GUI)")
            self.geometry("800x600")

            # Menu
            menubar = tk.Menu(self)
            filemenu = tk.Menu(menubar, tearoff=0)
            filemenu.add_command(label="Open", command=self.open_file)
            filemenu.add_command(label="Save", command=self.save_file)
            filemenu.add_separator()
            filemenu.add_command(label="Exit", command=self.quit)
            menubar.add_cascade(label="File", menu=filemenu)
            self.config(menu=menubar)

            # Text area
            self.text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD)
            self.text_area.pack(expand=1, fill=tk.BOTH)

            # Status bar
            self.status = tk.StringVar()
            self.status.set("Ready")
            status_bar = tk.Label(self, textvariable=self.status, bd=1, relief=tk.SUNKEN, anchor=tk.W)
            status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        def open_file(self):
            filename = filedialog.askopenfilename()
            if filename:
                try:
                    self.editor.open_file(filename)
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(tk.END, self.editor.get_buffer(filename))
                    self.editor.current_file = filename
                    self.status.set(f"Opened: {filename}")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        def save_file(self):
            filename = self.editor.current_file
            if not filename:
                filename = filedialog.asksaveasfilename()
                if not filename:
                    return
                self.editor.current_file = filename
            self.editor.edit_buffer(self.text_area.get(1.0, tk.END), filename)
            try:
                self.editor.save_file(filename)
                self.status.set(f"Saved: {filename}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

    gui = WumboGUI(editor)
    gui.mainloop()

# --- TUI Implementation ---

class WumboTUI:
    def __init__(self):
        self.editor = TextEditor()
        auto_register_all_plugins(self.editor)
        self.current_buffer = None
        self.buffers = self.editor.buffers

        # Main text area
        self.text_area = TextArea(
            text='',
            scrollbar=True,
            line_numbers=True,
            focus_on_click=True,
            wrap_lines=False
        )

        # Buffer list
        self.buffer_control = FormattedTextControl(self.get_buffer_list_text)
        self.buffer_window = Window(
            content=self.buffer_control,
            height=5,
            style="class:buffer-list",
            right_margins=[ScrollbarMargin(display_arrows=True)]
        )

        # Command palette
        self.command_palette = TextArea(
            height=1,
            prompt=': ',
            multiline=False,
            style="class:command-palette"
        )

        # Key bindings
        self.kb = self._setup_key_bindings()

        # Layout
        self.layout = Layout(
            HSplit([
                Frame(self.buffer_window, title="Buffers (F2 to switch)"),
                Frame(self.text_area, title="Editor (Ctrl-S to save, F5 to run command, F9 to launch GUI)"),
                Frame(self.command_palette, title="Command Palette (F5 to run)")
            ])
        )

        # Style
        self.style = Style.from_dict({
            'buffer-list': 'bg:#222222 #cccccc',
            'command-palette': 'bg:#333333 #ffffff',
            'frame.label': 'bg:#444444 #ffffff',
        })

        # Application
        self.application = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
            mouse_support=True
        )

        # Command palette state
        self.command_palette.buffer.accept_handler = self.run_command_from_palette

    def get_buffer_list_text(self):
        if not self.editor.buffers:
            return [('', 'No open buffers. Press F3 to open a file.')]
        result = []
        for fname in self.editor.buffers:
            marker = '[*]' if fname == self.editor.current_file else '[ ]'
            result.append(('class:buffer-list', f'{marker} {fname}\n'))
        return result

    def _setup_key_bindings(self):
        kb = KeyBindings()

        @kb.add('c-s')
        def _(event):
            "Save current buffer"
            self.save_current_buffer()

        @kb.add('f2')
        def _(event):
            "Switch buffer"
            self.switch_buffer_dialog()

        @kb.add('f3')
        def _(event):
            "Open file"
            self.open_file_dialog()

        @kb.add('f5')
        def _(event):
            "Run command from palette"
            self.application.layout.focus(self.command_palette)

        @kb.add('f9')
        def _(event):
            "Launch GUI"
            self.launch_gui_from_tui()

        @kb.add('escape')
        def _(event):
            "Return focus to editor"
            self.application.layout.focus(self.text_area)

        @kb.add('c-q')
        def _(event):
            "Quit"
            event.app.exit()

        return kb

    def save_current_buffer(self):
        filename = self.editor.current_file
        if not filename:
            message_dialog(title="Save Error", text="No file selected.").run()
            return
        self.editor.edit_buffer(self.text_area.text, filename)
        try:
            self.editor.save_file(filename)
            message_dialog(title="Saved", text=f"File saved: {filename}").run()
        except Exception as e:
            message_dialog(title="Save Error", text=str(e)).run()

    def switch_buffer_dialog(self):
        if not self.editor.buffers:
            message_dialog(title="Switch Buffer", text="No open buffers.").run()
            return
        buffer_names = list(self.editor.buffers.keys())
        buffer_str = "\n".join(f"{i+1}. {name}" for i, name in enumerate(buffer_names))
        choice = input_dialog(
            title="Switch Buffer",
            text=f"Buffers:\n{buffer_str}\nEnter buffer number:"
        ).run()
        if choice and choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(buffer_names):
                fname = buffer_names[idx]
                self.editor.current_file = fname
                self.text_area.text = self.editor.get_buffer(fname)

    def open_file_dialog(self):
        filename = input_dialog(title="Open File", text="Enter filename to open:").run()
        if filename:
            try:
                self.editor.open_file(filename)
                self.text_area.text = self.editor.get_buffer(filename)
                self.editor.current_file = filename
            except Exception as e:
                message_dialog(title="Open Error", text=str(e)).run()

    def run_command_from_palette(self, buf):
        cmd_line = buf.text.strip()
        if not cmd_line:
            self.application.layout.focus(self.text_area)
            return
        parts = cmd_line.split()
        cmd_name = parts[0]
        args = parts[1:]
        try:
            result = self.editor.run_command(cmd_name, *args)
            message_dialog(title="Command Result", text=str(result)).run()
        except Exception as e:
            message_dialog(title="Command Error", text=str(e)).run()
        finally:
            buf.text = ''
            self.application.layout.focus(self.text_area)

    def launch_gui_from_tui(self):
        # Launch the GUI in a separate thread so the TUI doesn't freeze
        threading.Thread(target=launch_gui, args=(self.editor,), daemon=True).start()
        message_dialog(title="GUI", text="Launched GUI in a new window.").run()

    def run(self):
        self.application.run()

if __name__ == "__main__":
    WumboTUI().run()
