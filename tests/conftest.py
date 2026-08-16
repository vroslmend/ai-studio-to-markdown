import pytest

from ai_studio_md import cli


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    """Keep the suite out of the real per-user config file.

    Any test that calls main() saves folder memory on success, which would
    otherwise point the user's dialogs at a pytest temp directory.
    """
    monkeypatch.setattr(cli, "config_path", lambda: tmp_path / "config.json")
