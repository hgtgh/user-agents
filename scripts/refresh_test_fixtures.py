#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from user_agents_updater.fixtures import fixture_filename
from user_agents_updater.http import fetch_json
from user_agents_updater.json_io import write_pretty_json
from user_agents_updater.providers_registry import ProviderRegistry

ROOT_DIR = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT_DIR / "tests" / "fixtures"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fixtures_meta: dict[str, dict[str, str]] = {}
    generated_filenames: set[str] = set()
    for provider in ProviderRegistry.default().all():
        for source_key, url in provider.source_urls().items():
            filename = fixture_filename(provider.name, source_key)
            generated_filenames.add(filename)
            source, payload = fetch_json(url)
            write_pretty_json(OUT_DIR / filename, payload)
            fixtures_meta[filename] = {
                "url": source,
                "provider": provider.name,
                "source_key": source_key,
            }
            print(f"- {OUT_DIR / filename}")

    for stale_file in OUT_DIR.glob("*.json"):
        if stale_file.name == "_meta.json":
            continue
        if stale_file.name not in generated_filenames:
            stale_file.unlink()
            print(f"- removed stale fixture: {stale_file}")

    write_pretty_json(OUT_DIR / "_meta.json", fixtures_meta)
    print(f"- {OUT_DIR / '_meta.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
