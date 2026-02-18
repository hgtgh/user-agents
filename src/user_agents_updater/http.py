from __future__ import annotations

import json
import random
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

DEFAULT_USER_AGENT_HEADER = "user-agents-updater/1.0"
USER_AGENTS_LIST_PATH = Path(__file__).resolve().parents[2] / "data" / "user-agents.json"


def _load_user_agent_pool(path: Path) -> tuple[str, ...]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ()

    if not isinstance(payload, list):
        return  tuple()

    return tuple(
        item.strip()
        for item in payload
        if isinstance(item, str) and item.strip()
    )

USER_AGENT_POOL: tuple[str, ...] = _load_user_agent_pool(USER_AGENTS_LIST_PATH)

def _pick_user_agent(pool: tuple[str, ...] = USER_AGENT_POOL) -> str:
    """
    Selects a random UA if available, otherwise returns the fallback.
    `pool` is injectable (practical for tests).
    """
    return random.choice(pool) if pool else DEFAULT_USER_AGENT_HEADER


def fetch_json(url: str) -> tuple[str, object]:
    try:
        req = Request(url, headers={"User-Agent": _pick_user_agent()})
        with urlopen(req, timeout=30) as response:
            payload = response.read().decode("utf-8", errors="replace")
        return url, json.loads(payload)
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as err:
        raise RuntimeError(f"Unable to fetch JSON from endpoint '{url}': {err}") from err
