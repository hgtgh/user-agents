from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections.abc import Sequence

from .fixtures import fixture_filename
from .http import fetch_json
from .json_io import write_pretty_json
from .models import JsonFetcher
from .providers_registry import ProviderRegistry
from .service import UserAgentService

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATA_DIR = REPO_ROOT / "data"
DEFAULT_FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"

LIST_FILENAME = "user-agents.json"
METADATA_FILENAME = "user-agents-metadata.json"
FIXTURES_META_FILENAME = "_meta.json"


def utc_now_isoformat() -> str:
    """Return the current UTC time as a second-precision ISO-8601 string ending in ``Z``."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_dataset(
    fetcher: JsonFetcher,
    *,
    now: str | None = None,
) -> tuple[dict[str, object], list[str]]:
    """Resolve browser versions and render user-agents from ``fetcher``.

    Returns the metadata payload and the flat list of rendered user-agent strings.
    The ``now`` argument is injectable so the timestamp is deterministic in tests.
    """
    resolved_versions, sources, user_agents = UserAgentService().generate(fetcher)
    metadata: dict[str, object] = {
        "updated_at": now or utc_now_isoformat(),
        "sources": sources,
        "resolved_versions": resolved_versions.to_dict(),
        "user_agents": user_agents,
    }
    user_agent_strings = [entry["user_agent"] for entry in user_agents]
    return metadata, user_agent_strings


def write_dataset(
    out_dir: str | Path,
    fetcher: JsonFetcher = fetch_json,
    *,
    now: str | None = None,
) -> tuple[Path, Path, int]:
    """Write the plain list and the metadata-rich dataset into ``out_dir``.

    Returns ``(list_path, metadata_path, user_agent_count)``.
    """
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)

    metadata, user_agent_strings = build_dataset(fetcher, now=now)
    list_path = target / LIST_FILENAME
    metadata_path = target / METADATA_FILENAME
    write_pretty_json(list_path, user_agent_strings)
    write_pretty_json(metadata_path, metadata)
    return list_path, metadata_path, len(user_agent_strings)


def refresh_fixtures(
    out_dir: str | Path,
    fetcher: JsonFetcher = fetch_json,
    *,
    keep_stale: bool = False,
) -> dict[str, dict[str, str]]:
    """Regenerate the provider HTTP fixtures used by the test-suite.

    Fixtures no longer produced by any provider are deleted unless ``keep_stale``
    is true. Returns the ``_meta.json`` filename -> metadata mapping.
    """
    target = Path(out_dir)
    target.mkdir(parents=True, exist_ok=True)

    generated_filenames: set[str] = set()
    fixtures_meta: dict[str, dict[str, str]] = {}

    for provider in ProviderRegistry.default().all():
        for source_key, url in provider.source_urls().items():
            filename = fixture_filename(provider.name, source_key)
            generated_filenames.add(filename)
            source, payload = fetcher(url)
            write_pretty_json(target / filename, payload)
            fixtures_meta[filename] = {
                "url": source,
                "provider": provider.name,
                "source_key": source_key,
            }

    if not keep_stale:
        for stale_file in target.glob("*.json"):
            if stale_file.name == FIXTURES_META_FILENAME or stale_file.name in generated_filenames:
                continue
            stale_file.unlink()

    write_pretty_json(target / FIXTURES_META_FILENAME, fixtures_meta)
    return fixtures_meta


def default_data_dir() -> Path:
    """Repo ``data`` dir when running from a checkout, otherwise ``./data``."""
    if (REPO_ROOT / "src" / "user_agents_updater").is_dir():
        return DEFAULT_DATA_DIR
    return Path.cwd() / "data"


def default_fixtures_dir() -> Path:
    """Repo ``tests/fixtures`` dir when running from a checkout, otherwise ``./tests/fixtures``."""
    if (REPO_ROOT / "src" / "user_agents_updater").is_dir():
        return DEFAULT_FIXTURES_DIR
    return Path.cwd() / "tests" / "fixtures"


def build_update_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="user-agents-update",
        description="Regenerate the user-agents dataset from official browser release feeds.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(default_data_dir()),
        help="Directory for user-agents.json and user-agents-metadata.json (default: %(default)s).",
    )
    return parser


def build_refresh_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="user-agents-refresh-fixtures",
        description="Refresh the HTTP fixtures used by the test-suite from the live provider endpoints.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(default_fixtures_dir()),
        help="Directory for the generated fixtures (default: %(default)s).",
    )
    parser.add_argument(
        "--keep-stale",
        action="store_true",
        help="Keep fixture files that are no longer generated by any provider.",
    )
    return parser


def main_update(argv: Sequence[str] | None = None) -> int:
    args = build_update_parser().parse_args(argv)

    print("Updating user-agents...", flush=True)
    list_path, metadata_path, count = write_dataset(args.output_dir)
    print(f"Done: {count} user-agents", flush=True)
    print(f"- {list_path}", flush=True)
    print(f"- {metadata_path}", flush=True)
    return 0


def main_refresh_fixtures(argv: Sequence[str] | None = None) -> int:
    args = build_refresh_parser().parse_args(argv)

    fixtures_meta = refresh_fixtures(args.output_dir, keep_stale=args.keep_stale)
    out_dir = Path(args.output_dir)
    for filename in fixtures_meta:
        print(f"- {out_dir / filename}", flush=True)
    print(f"- {out_dir / FIXTURES_META_FILENAME}", flush=True)
    return 0
