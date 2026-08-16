import json
from pathlib import Path

import pytest

from ai_studio_md.cli import main, resolve_io

SAMPLE = {
    "runSettings": {"model": "models/gemini-3.1-pro-preview", "temperature": 1.0},
    "chunkedPrompt": {
        "chunks": [
            {"role": "user", "text": "hello", "createTime": "2026-05-22T12:17:00.000Z"},
            {"role": "model", "text": "reasoning here", "isThought": True},
            {"role": "model", "text": "hi back"},
        ]
    },
}


class FakePicker:
    """Records calls so tests can prove the picker was or wasn't consulted."""

    def __init__(self, input_choice=None, output_choice=None):
        self.input_choice = input_choice
        self.output_choice = output_choice
        self.calls = []

    def choose_input(self, initial_dir):
        self.calls.append(("input", initial_dir))
        return self.input_choice

    def choose_output(self, initial_dir, default_name):
        self.calls.append(("output", initial_dir, default_name))
        return self.output_choice


@pytest.fixture
def export(tmp_path):
    path = tmp_path / "My Chat"
    path.write_text(json.dumps(SAMPLE), encoding="utf-8")
    return path


def test_explicit_paths_never_consult_the_picker():
    picker = FakePicker()

    chosen = resolve_io("in.json", "out.md", picker, {})

    assert chosen == ("in.json", "out.md")
    assert picker.calls == []


def test_an_input_without_an_output_lands_beside_the_input():
    picker = FakePicker()

    _, output = resolve_io(str(Path("downloads") / "My Chat"), None, picker, {})

    assert output == str(Path("downloads") / "My Chat.md")
    assert picker.calls == []


def test_a_json_extension_is_replaced_rather_than_appended():
    _, output = resolve_io(str(Path("d") / "chat.json"), None, FakePicker(), {})

    assert output == str(Path("d") / "chat.md")


def test_bare_invocation_asks_the_picker_for_both_paths():
    picker = FakePicker(input_choice="picked.json", output_choice="saved.md")

    assert resolve_io(None, None, picker, {}) == ("picked.json", "saved.md")


def test_picker_opens_at_the_remembered_folders():
    picker = FakePicker(input_choice="a", output_choice="b")

    resolve_io(None, None, picker, {"input_dir": "D:/Downloads", "output_dir": "D:/Notes"})

    assert picker.calls[0] == ("input", "D:/Downloads")
    assert picker.calls[1][1] == "D:/Notes"


def test_the_save_dialog_is_prefilled_from_the_input_filename():
    picker = FakePicker(input_choice=str(Path("x") / "My Chat"), output_choice="b")

    resolve_io(None, None, picker, {})

    assert picker.calls[1][2] == "My Chat.md"


def test_cancelling_the_input_dialog_stops_without_asking_for_output():
    picker = FakePicker(input_choice=None)

    assert resolve_io(None, None, picker, {}) is None
    assert [c[0] for c in picker.calls] == ["input"]


def test_cancelling_the_save_dialog_stops():
    picker = FakePicker(input_choice="a.json", output_choice=None)

    assert resolve_io(None, None, picker, {}) is None


def test_converts_an_export_end_to_end(export, tmp_path):
    out = tmp_path / "out.md"

    code = main([str(export), "-o", str(out)])

    assert code == 0
    written = out.read_text(encoding="utf-8")
    assert "hello" in written
    assert "hi back" in written


def test_thoughts_are_excluded_unless_the_flag_is_given(export, tmp_path):
    out = tmp_path / "out.md"
    main([str(export), "-o", str(out)])

    assert "reasoning here" not in out.read_text(encoding="utf-8")


def test_the_thoughts_flag_includes_them(export, tmp_path):
    out = tmp_path / "out.md"
    main([str(export), "-t", "-o", str(out)])

    assert "reasoning here" in out.read_text(encoding="utf-8")


def test_drive_pointers_stay_out_of_the_output_unless_requested(tmp_path):
    export = tmp_path / "chat"
    export.write_text(
        json.dumps(
            {
                "runSettings": {},
                "chunkedPrompt": {"chunks": [{"driveImage": {"id": "secret1"}, "role": "user"}]},
            }
        ),
        encoding="utf-8",
    )
    out = tmp_path / "out.md"

    main([str(export), "-o", str(out)])
    assert "secret1" not in out.read_text(encoding="utf-8")

    main([str(export), "--drive-links", "-o", str(out)])
    assert "secret1" in out.read_text(encoding="utf-8")


def test_a_missing_input_file_reports_an_error(tmp_path, capsys):
    code = main([str(tmp_path / "absent"), "-o", str(tmp_path / "o.md")])

    assert code != 0
    assert "not find" in capsys.readouterr().err.lower()


def test_a_file_that_is_not_json_reports_a_parse_error(tmp_path, capsys):
    bad = tmp_path / "bad"
    bad.write_text("this is not json", encoding="utf-8")

    code = main([str(bad), "-o", str(tmp_path / "o.md")])

    assert code != 0
    assert "json" in capsys.readouterr().err.lower()


def test_a_successful_run_remembers_both_folders(tmp_path, monkeypatch, export):
    settings_file = tmp_path / "cfg" / "config.json"
    monkeypatch.setattr("ai_studio_md.cli.config_path", lambda: settings_file)
    out = tmp_path / "notes" / "out.md"
    out.parent.mkdir()

    main([str(export), "-o", str(out)])

    saved = json.loads(settings_file.read_text(encoding="utf-8"))
    assert saved["input_dir"] == str(export.parent)
    assert saved["output_dir"] == str(out.parent)


def test_output_directories_are_created_when_missing(export, tmp_path):
    out = tmp_path / "brand" / "new" / "out.md"

    assert main([str(export), "-o", str(out)]) == 0
    assert out.exists()


def test_cancelling_the_picker_exits_quietly(monkeypatch, capsys):
    monkeypatch.setattr("ai_studio_md.cli.select_picker", lambda: FakePicker(input_choice=None))

    code = main([])

    assert code != 0
    assert "cancel" in capsys.readouterr().err.lower()
