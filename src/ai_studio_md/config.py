"""Remember which folders the picker last opened.

Purely a convenience: every failure mode here degrades to "ask from scratch"
rather than interrupting a conversion.
"""

import json
import os
import sys
from pathlib import Path

APP_DIR = "ai-studio-md"


def config_path():
    """Per-user config location for the current platform."""
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming"
    else:
        base = os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config"
    return Path(base) / APP_DIR / "config.json"


def load_config(path=None):
    path = Path(path) if path else config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            settings = json.load(f)
    except (OSError, ValueError):
        return {}
    return settings if isinstance(settings, dict) else {}


def save_config(path, settings):
    path = Path(path)
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except OSError:
        pass  # Folder memory is optional; never fail a conversion over it.
