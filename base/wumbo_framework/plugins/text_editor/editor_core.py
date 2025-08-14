"""
editor_core.py

A minimal text editor core for the Wumbo framework, designed to natively support
other plugins (algorithm wizard, data structure wizard, LSP, etc.).

Features:
- Open, edit, and save text files.
- Register and invoke plugin commands.
- Integrate with LSP for code intelligence (via plugin).
- Simple in-memory buffer management.


"""

from typing import Callable, Dict, List, Optional

class TextEditor:
    """
    Minimal text editor core for Wumbo.

    Attributes:
        buffers (Dict[str, str]): Mapping of filename to file contents.
        commands (Dict[str, Callable]): Registered commands from plugins or core.
        current_file (Optional[str]): The currently active file.
    """

    def __init__(self):
        self.buffers: Dict[str, str] = {}
        self.commands: Dict[str, Callable] = {}
        self.current_file: Optional[str] = None

    def open_file(self, filename: str) -> None:
        """
        Open a file and load its contents into the buffer.

        Args:
            filename (str): Path to the file to open.
        """
        with open(filename, 'r', encoding='utf-8') as f:
            self.buffers[filename] = f.read()
        self.current_file = filename

    def save_file(self, filename: Optional[str] = None) -> None:
        """
        Save the contents of the buffer to disk.

        Args:
            filename (str, optional): File to save. If None, saves the current file.
        """
        target = filename or self.current_file
        if not target or target not in self.buffers:
            raise ValueError("No file to save.")
        with open(target, 'w', encoding='utf-8') as f:
            f.write(self.buffers[target])

    def edit_buffer(self, new_content: str, filename: Optional[str] = None) -> None:
        """
        Replace the contents of a buffer.

        Args:
            new_content (str): The new content for the buffer.
            filename (str, optional): Buffer to edit. If None, edits the current file.
        """
        target = filename or self.current_file
        if not target:
            raise ValueError("No file selected for editing.")
        self.buffers[target] = new_content

    def get_buffer(self, filename: Optional[str] = None) -> str:
        """
        Get the contents of a buffer.

        Args:
            filename (str, optional): Buffer to retrieve. If None, uses the current file.

        Returns:
            str: The contents of the buffer.
        """
        target = filename or self.current_file
        if not target or target not in self.buffers:
            raise ValueError("No buffer found for the specified file.")
        return self.buffers[target]

    def register_command(self, name: str, func: Callable) -> None:
        """
        Register a command (from a plugin or core) with the editor.

        Args:
            name (str): Command name.
            func (Callable): Function to execute for the command.
        """
        self.commands[name] = func

    def run_command(self, name: str, *args, **kwargs):
        """
        Run a registered command.

        Args:
            name (str): Command name.
            *args: Positional arguments for the command.
            **kwargs: Keyword arguments for the command.

        Returns:
            Any: The result of the command.
        """
        if name in self.commands:
            return self.commands[name](*args, **kwargs)
        raise ValueError(f"Command '{name}' not found.")

    def list_commands(self) -> List[str]:
        """
        List all registered commands.

        Returns:
            List[str]: Names of all registered commands.
        """
        return list(self.commands.keys())

    def close_file(self, filename: Optional[str] = None) -> None:
        """
        Close a file buffer.

        Args:
            filename (str, optional): Buffer to close. If None, closes the current file.
        """
        target = filename or self.current_file
        if target and target in self.buffers:
            del self.buffers[target]
            if self.current_file == target:
                self.current_file = None

# Example usage and plugin integration (for demonstration/testing)
if __name__ == "__main__":
    editor = TextEditor()
    # Register a sample command
    def hello_command():
        print("Hello from plugin!")
    editor.register_command("hello", hello_command)

    print("Registered commands:", editor.list_commands())
    editor.run_command("hello")
