from __future__ import annotations

import json
from pathlib import Path

from user_agents_updater.fixtures import fixture_filename

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
FIXTURES_META = json.loads((FIXTURES_DIR / "_meta.json").read_text(encoding="utf-8"))


def load_fixture(name: str) -> object:
    return json.loads((FIXTURES_DIR / name).read_text(encoding="utf-8"))


def fixture_url(name: str) -> str:
    return FIXTURES_META[name]["url"]


def fixture_name(provider_name: str, source_key: str) -> str:
    return fixture_filename(provider_name, source_key)


def load_provider_fixture(provider_name: str, source_key: str) -> object:
    return load_fixture(fixture_name(provider_name, source_key))
