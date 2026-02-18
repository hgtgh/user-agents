#!/usr/bin/env python3
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

from user_agents_updater import fetch_json
from user_agents_updater.json_io import write_pretty_json
from user_agents_updater.service import UserAgentService

OUT_DIR = ROOT_DIR / "data"
OUT_LIST_FILE = OUT_DIR / "user-agents.json"
OUT_METADATA_FILE = OUT_DIR / "user-agents-metadata.json"


def main() -> int:
    print("Updating user-agents...", flush=True)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    service = UserAgentService()
    resolved_versions, sources, user_agents = service.generate(fetch_json)

    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    user_agents_payload = {
        "updated_at": now,
        "sources": sources,
        "resolved_versions": resolved_versions.to_dict(),
        "user_agents": user_agents,
    }
    user_agents_list_payload = [
        entry["user_agent"]
        for entry in user_agents_payload["user_agents"]
    ]

    write_pretty_json(OUT_LIST_FILE, user_agents_list_payload)
    write_pretty_json(OUT_METADATA_FILE, user_agents_payload)

    print(f"Done: {len(user_agents)} user-agents", flush=True)
    print(f"- {OUT_LIST_FILE}", flush=True)
    print(f"- {OUT_METADATA_FILE}", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(1)
