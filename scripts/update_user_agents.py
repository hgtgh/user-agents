#!/usr/bin/env python3
"""Entry point that regenerates the user-agents dataset.

Thin wrapper so the tool runs straight from a checkout (``python3
scripts/update_user_agents.py``) or via the ``user-agents-update`` console
script once the package is installed.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the src-layout package importable without relying on an external PYTHONPATH.
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from user_agents_updater.cli import main_update  # noqa: E402


if __name__ == "__main__":
    try:
        raise SystemExit(main_update())
    except Exception as exc:  # noqa: BLE001 - top-level guard for standalone runs
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
