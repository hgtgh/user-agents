from __future__ import annotations

import json
from pathlib import Path


def write_pretty_json(path: Path, data: object) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
