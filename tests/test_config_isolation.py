"""The suite must never write to the config file a real user depends on."""

import json

from ai_studio_md import cli
from ai_studio_md.config import config_path


def test_running_the_cli_does_not_touch_the_real_user_config(tmp_path, monkeypatch):
    real = tmp_path / "real" / "config.json"
    real.parent.mkdir()
    real.write_text(json.dumps({"input_dir": "D:/Notes"}), encoding="utf-8")
    monkeypatch.setattr("ai_studio_md.config.config_path", lambda: real)

    export = tmp_path / "chat"
    export.write_text(
        json.dumps({"runSettings": {}, "chunkedPrompt": {"chunks": [{"role": "user", "text": "hi"}]}}),
        encoding="utf-8",
    )
    cli.main([str(export), "-o", str(tmp_path / "out.md")])

    assert json.loads(real.read_text(encoding="utf-8")) == {"input_dir": "D:/Notes"}


def test_the_autouse_fixture_redirects_config_path_away_from_the_user(tmp_path):
    assert cli.config_path() != config_path()
