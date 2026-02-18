from __future__ import annotations


def parse_semver_like(value: str) -> tuple[int, ...]:
    parts = value.split(".")

    if not all(part.isdigit() for part in parts):
        return ()

    return tuple(map(int, parts))


def major_version(value: str) -> str:
    return value.split(".", 1)[0]
