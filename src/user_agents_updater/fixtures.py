from __future__ import annotations


def fixture_filename(provider_name: str, source_key: str) -> str:
    if source_key == "default":
        return f"{provider_name}.json"
    return f"{provider_name}_{source_key}.json"
