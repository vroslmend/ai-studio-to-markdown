import json
from pathlib import Path

from ai_studio_md.config import config_path, load_config, save_config


def test_returns_empty_settings_when_no_config_file_exists(tmp_path):
    assert load_config(tmp_path / "nope.json") == {}


def test_corrupt_config_is_ignored_rather_than_crashing(tmp_path):
    broken = tmp_path / "config.json"
    broken.write_text("{not json at all", encoding="utf-8")

    assert load_config(broken) == {}


def test_saved_settings_round_trip(tmp_path):
    path = tmp_path / "config.json"

    save_config(path, {"input_dir": "C:/Downloads", "output_dir": "D:/Notes"})

    assert load_config(path) == {"input_dir": "C:/Downloads", "output_dir": "D:/Notes"}


def test_saving_creates_the_config_directory(tmp_path):
    path = tmp_path / "nested" / "deeper" / "config.json"

    save_config(path, {"input_dir": "x"})

    assert json.loads(path.read_text(encoding="utf-8")) == {"input_dir": "x"}


def test_saving_never_raises_when_the_location_is_unwritable(tmp_path):
    """Losing folder memory must not break a conversion."""
    blocker = tmp_path / "afile"
    blocker.write_text("occupied", encoding="utf-8")

    save_config(blocker / "config.json", {"input_dir": "x"})


def test_config_lives_under_appdata_on_windows(monkeypatch):
    monkeypatch.setattr("sys.platform", "win32")
    monkeypatch.setenv("APPDATA", r"C:\Users\Example\AppData\Roaming")

    assert Path(r"C:\Users\Example\AppData\Roaming") in config_path().parents
    assert config_path().name == "config.json"


def test_config_respects_xdg_config_home_elsewhere(monkeypatch):
    monkeypatch.setattr("sys.platform", "linux")
    monkeypatch.setenv("XDG_CONFIG_HOME", "/home/example/.config")

    assert Path("/home/example/.config") in config_path().parents
