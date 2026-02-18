import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from user_agents_updater.http import (  # noqa: E402
    DEFAULT_USER_AGENT_HEADER,
    _load_user_agent_pool,
    _pick_user_agent,
    fetch_json,
)


class _FakeResponse:
    def __init__(self, payload: str) -> None:
        self._payload = payload.encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self) -> bytes:
        return self._payload


class HttpTests(unittest.TestCase):
    def test_load_user_agent_pool_filters_invalid_entries(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "user-agents.json"
            path.write_text('[" UA1 ", "", 42, "UA2"]', encoding="utf-8")
            self.assertEqual(_load_user_agent_pool(path), ("UA1", "UA2"))

    def test_pick_user_agent_falls_back_when_pool_is_empty(self):
        self.assertEqual(_pick_user_agent(()), DEFAULT_USER_AGENT_HEADER)

    def test_pick_user_agent_uses_random_choice_when_pool_is_not_empty(self):
        with patch("user_agents_updater.http.random.choice", return_value="UA2") as mocked_choice:
            self.assertEqual(_pick_user_agent(("UA1", "UA2")), "UA2")
            mocked_choice.assert_called_once_with(("UA1", "UA2"))

    def test_fetch_json_returns_source_and_payload(self):
        with patch("user_agents_updater.http.urlopen", return_value=_FakeResponse('{"ok": true}')):
            source, payload = fetch_json("https://example.com/data.json")
        self.assertEqual(source, "https://example.com/data.json")
        self.assertEqual(payload, {"ok": True})

    def test_fetch_json_wraps_errors(self):
        with patch("user_agents_updater.http.urlopen", side_effect=TimeoutError("timeout")):
            with self.assertRaises(RuntimeError):
                fetch_json("https://example.com/data.json")


if __name__ == "__main__":
    unittest.main()
