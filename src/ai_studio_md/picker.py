"""Ask the user for input and output paths.

Two interchangeable pickers with the same two methods. `tkinter` is imported
inside functions only, so machines without it can still run scripted
conversions that never touch a GUI.
"""

import sys
from pathlib import Path

INSTALL_HINTS = {
    "linux": "install the 'python3-tk' package (Debian/Ubuntu) or 'python3-tkinter' (Fedora)",
    "darwin": "install tk support, e.g. 'brew install python-tk'",
}
DEFAULT_HINT = "no graphical file dialog is available"


def install_hint():
    return INSTALL_HINTS.get(sys.platform, DEFAULT_HINT)


def gui_available():
    """True only if a Tk window can actually be created right now.

    Probing by construction rather than by sniffing DISPLAY, which is unset on
    Windows even though dialogs work there.
    """
    try:
        import tkinter
    except Exception:
        return False
    if tkinter is None:
        return False
    try:
        root = tkinter.Tk()
        root.withdraw()
        root.destroy()
    except Exception:
        return False
    return True


class GuiPicker:
    def _root(self):
        import tkinter

        root = tkinter.Tk()
        root.withdraw()
        # Tk on macOS otherwise opens dialogs behind the terminal.
        root.attributes("-topmost", True)
        return root

    def choose_input(self, initial_dir):
        from tkinter import filedialog

        root = self._root()
        try:
            # Drive downloads arrive without an extension, so no filter by default.
            chosen = filedialog.askopenfilename(
                title="Select AI Studio export",
                initialdir=initial_dir or None,
                filetypes=[("All files", "*.*"), ("JSON", "*.json")],
            )
        finally:
            root.destroy()
        return chosen or None

    def choose_output(self, initial_dir, default_name):
        from tkinter import filedialog

        root = self._root()
        try:
            chosen = filedialog.asksaveasfilename(
                title="Save Markdown as",
                initialdir=initial_dir or None,
                initialfile=default_name,
                defaultextension=".md",
                filetypes=[("Markdown", "*.md"), ("All files", "*.*")],
            )
        finally:
            root.destroy()
        return chosen or None


class TerminalPicker:
    def __init__(self, io=input):
        self._io = io

    def _ask(self, prompt):
        try:
            return self._io(prompt).strip().strip('"').strip("'")
        except (EOFError, KeyboardInterrupt):
            return ""

    def choose_input(self, initial_dir):
        where = f" [{initial_dir}]" if initial_dir else ""
        return self._ask(f"AI Studio export{where} (drag the file here): ") or None

    def choose_output(self, initial_dir, default_name):
        default = str(Path(initial_dir) / default_name) if initial_dir else default_name
        answer = self._ask(f"Save Markdown to [{default}]: ")
        if not answer:
            return str(Path(default))
        if Path(answer).is_dir():
            return str(Path(answer) / default_name)
        return answer


def select_picker():
    return GuiPicker() if gui_available() else TerminalPicker()
