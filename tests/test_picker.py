import subprocess
import sys

import pytest

from ai_studio_md.picker import TerminalPicker, gui_available, install_hint, select_picker


class FakeIO:
    def __init__(self, answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt=""):
        self.prompts.append(prompt)
        if not self.answers:
            raise AssertionError("asked for more input than the test provided")
        return self.answers.pop(0)


def test_gui_is_reported_unavailable_when_tkinter_is_missing(monkeypatch):
    """Linux distros routinely ship Python without python3-tk."""
    monkeypatch.setitem(sys.modules, "tkinter", None)

    assert gui_available() is False


def test_terminal_picker_is_selected_when_there_is_no_gui(monkeypatch):
    monkeypatch.setattr("ai_studio_md.picker.gui_available", lambda: False)

    assert isinstance(select_picker(), TerminalPicker)


def test_install_hint_names_the_right_package_per_platform(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    assert "python3-tk" in install_hint()

    monkeypatch.setattr("sys.platform", "darwin")
    assert "python-tk" in install_hint()


def test_terminal_picker_strips_quotes_windows_adds_when_dragging_a_file():
    picker = TerminalPicker(io=FakeIO(['"C:\\Users\\Example\\Downloads\\chat"']))

    assert picker.choose_input("") == "C:\\Users\\Example\\Downloads\\chat"


def test_terminal_picker_returns_none_when_input_is_left_blank():
    assert TerminalPicker(io=FakeIO([""])).choose_input("") is None


def test_terminal_picker_offers_a_default_output_accepted_with_enter(tmp_path):
    picker = TerminalPicker(io=FakeIO([""]))

    assert picker.choose_output(str(tmp_path), "chat.md") == str(tmp_path / "chat.md")


def test_terminal_picker_treats_a_bare_directory_as_a_destination_folder(tmp_path):
    picker = TerminalPicker(io=FakeIO([str(tmp_path)]))

    assert picker.choose_output("", "chat.md") == str(tmp_path / "chat.md")


def test_importing_the_cli_does_not_pull_in_tkinter():
    """A scripted run on a machine without tk must not crash on import."""
    code = "import ai_studio_md.cli, sys; print('tkinter' in sys.modules)"
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd="src",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.strip() == "False"
