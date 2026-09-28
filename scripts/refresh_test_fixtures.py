#!/usr/bin/env python3
"""Entry point that refreshes the test-suite HTTP fixtures.

Thin wrapper so the tool runs straight from a checkout (``python3
scripts/refresh_test_fixtures.py``) or via the ``user-agents-refresh-fixtures``
console script once the package is installed.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make the src-layout package importable without relying on an external PYTHONPATH.
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from user_agents_updater.cli import main_refresh_fixtures  # noqa: E402


if __name__ == "__main__":
    try:
        raise SystemExit(main_refresh_fixtures())
    except Exception as exc:  # noqa: BLE001 - top-level guard for standalone runs
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
