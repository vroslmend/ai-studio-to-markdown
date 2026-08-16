#!/usr/bin/env python3
"""Run the tool straight from a clone, without installing it.

    python extract.py                    # pick the files interactively
    python extract.py chat.json -o out.md

Kept so the original entry point still works; the code lives in src/ai_studio_md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from ai_studio_md.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
