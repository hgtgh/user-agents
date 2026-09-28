import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from user_agents_updater.cli import (  # noqa: E402
    DEFAULT_DATA_DIR,
    build_dataset,
    build_refresh_parser,
    build_update_parser,
    main_refresh_fixtures,
    main_update,
    refresh_fixtures,
    utc_now_isoformat,
    write_dataset,
)
from user_agents_updater.fixtures import fixture_filename  # noqa: E402
from user_agents_updater.providers_registry import ProviderRegistry  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"


def _fixture_fetcher():
    """Serve the checked-in fixtures instead of hitting the live endpoints."""
    meta = json.loads((FIXTURES_DIR / "_meta.json").read_text(encoding="utf-8"))
    by_url = {entry["url"]: name for name, entry in meta.items()}

    def fetcher(url: str):
        if url not in by_url:
            raise RuntimeError(f"Unexpected URL: {url}")
        payload = json.loads((FIXTURES_DIR / by_url[url]).read_text(encoding="utf-8"))
        return url, payload

    return fetcher


def _expected_fixture_filenames() -> set[str]:
    names = set()
    for provider in ProviderRegistry.default().all():
        for source_key in provider.source_urls():
            names.add(fixture_filename(provider.name, source_key))
    return names


class BuildDatasetTests(unittest.TestCase):
    def test_build_dataset_returns_metadata_and_flat_list(self):
        metadata, user_agent_strings = build_dataset(_fixture_fetcher())

        self.assertIsInstance(metadata["updated_at"], str)
        self.assertIn("sources", metadata)
        self.assertIn("resolved_versions", metadata)
        user_agents_payload = metadata["user_agents"]
        self.assertEqual(len(user_agents_payload), len(user_agent_strings))
        self.assertTrue(all(isinstance(ua, str) and ua for ua in user_agent_strings))
        first_payload: dict = user_agents_payload[0]
        self.assertEqual(str(first_payload["user_agent"]), user_agent_strings[0])

    def test_build_dataset_honours_injected_timestamp(self):
        metadata, _ = build_dataset(_fixture_fetcher(), now="2020-01-01T00:00:00Z")
        self.assertEqual(metadata["updated_at"], "2020-01-01T00:00:00Z")

    def test_utc_now_isoformat_is_z_terminated_iso8601(self):
        self.assertRegex(utc_now_isoformat(), r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


class WriteDatasetTests(unittest.TestCase):
    def test_write_dataset_writes_both_files_and_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            list_path, metadata_path, count = write_dataset(tmp, _fixture_fetcher())

            self.assertGreater(count, 0)
            self.assertTrue(list_path.is_file())
            self.assertTrue(metadata_path.is_file())

            ua_list = json.loads(list_path.read_text(encoding="utf-8"))
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(len(ua_list), count)
            self.assertEqual(len(metadata["user_agents"]), count)

    def test_write_dataset_creates_missing_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            nested = Path(tmp) / "a" / "b" / "c"
            list_path, _, _ = write_dataset(nested, _fixture_fetcher())
            self.assertTrue(list_path.is_file())


class UpdateCliTests(unittest.TestCase):
    def test_update_parser_output_dir_defaults_to_repo_data_dir(self):
        args = build_update_parser().parse_args([])
        self.assertEqual(args.output_dir, str(DEFAULT_DATA_DIR))

    def test_update_parser_accepts_output_dir_flag(self):
        args = build_update_parser().parse_args(["--output-dir", "/tmp/custom"])
        self.assertEqual(args.output_dir, "/tmp/custom")

    def test_main_update_writes_to_output_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main_update(["--output-dir", tmp])

            self.assertEqual(code, 0)
            self.assertIn("Done:", stdout.getvalue())
            self.assertTrue((Path(tmp) / "user-agents.json").is_file())
            self.assertTrue((Path(tmp) / "user-agents-metadata.json").is_file())


class RefreshFixturesTests(unittest.TestCase):
    def test_refresh_fixtures_writes_all_provider_fixtures_and_meta(self):
        expected = _expected_fixture_filenames()
        self.assertTrue(expected)

        with tempfile.TemporaryDirectory() as tmp:
            meta = refresh_fixtures(tmp, _fixture_fetcher())
            out = Path(tmp)

            self.assertEqual(set(meta.keys()), expected)
            for name in expected:
                self.assertTrue((out / name).is_file())
            self.assertTrue((out / "_meta.json").is_file())

    def test_refresh_fixtures_removes_stale_files_by_default(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            stale = out / "stale-provider.json"
            stale.write_text("{}", encoding="utf-8")
            (out / "_meta.json").write_text("{}", encoding="utf-8")

            refresh_fixtures(tmp, _fixture_fetcher())

            self.assertFalse(stale.exists())
            self.assertTrue((out / "_meta.json").exists())

    def test_refresh_fixtures_keeps_stale_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            stale = out / "stale-provider.json"
            stale.write_text("{}", encoding="utf-8")

            refresh_fixtures(tmp, _fixture_fetcher(), keep_stale=True)

            self.assertTrue(stale.exists())

    def test_main_refresh_fixtures_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmp:
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main_refresh_fixtures(["--output-dir", tmp])
            self.assertEqual(code, 0)
            self.assertIn("- ", stdout.getvalue())
            self.assertTrue((Path(tmp) / "_meta.json").is_file())

    def test_refresh_parser_accepts_keep_stale_flag(self):
        args = build_refresh_parser().parse_args(["--output-dir", "/tmp/x", "--keep-stale"])
        self.assertTrue(args.keep_stale)
        self.assertEqual(args.output_dir, "/tmp/x")


class ScriptBootstrappingTests(unittest.TestCase):
    """Regression tests for direct execution without an external PYTHONPATH."""

    def _run_script(self, script_name: str) -> subprocess.CompletedProcess:
        env = os.environ.copy()
        env.pop("PYTHONPATH", None)
        return subprocess.run(
            [sys.executable, str(REPO_ROOT / "scripts" / script_name), "--help"],
            cwd=str(REPO_ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
        )

    def test_update_script_runs_without_pythonpath(self):
        result = self._run_script("update_user_agents.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("usage:", result.stdout)

    def test_refresh_fixtures_script_runs_without_pythonpath(self):
        result = self._run_script("refresh_test_fixtures.py")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("usage:", result.stdout)


if __name__ == "__main__":
    unittest.main()
