import unittest

from _fixtures import load_provider_fixture
from user_agents_updater.providers.chrome import CHROME_VARIANTS  # noqa: E402
from user_agents_updater.providers.edge import EDGE_VARIANTS  # noqa: E402
from user_agents_updater.providers.firefox import FIREFOX_VARIANTS  # noqa: E402
from user_agents_updater.providers.safari import SAFARI_VARIANTS  # noqa: E402
from user_agents_updater.providers_registry import ProviderRegistry  # noqa: E402
from user_agents_updater.service import UserAgentService  # noqa: E402


class ServiceTests(unittest.TestCase):
    def test_generate_user_agents_matches_provider_variants(self):
        fixtures_by_url: dict[str, object] = {}
        for provider in ProviderRegistry.default().all():
            for source_key, url in provider.source_urls().items():
                fixtures_by_url[url] = load_provider_fixture(provider.name, source_key)

        def fake_fetcher(url):
            return url, fixtures_by_url[url]

        resolved_versions, _, user_agents = UserAgentService().generate(fake_fetcher)

        variants_by_browser = {
            "chrome": CHROME_VARIANTS,
            "edge": EDGE_VARIANTS,
            "firefox": FIREFOX_VARIANTS,
            "safari": SAFARI_VARIANTS,
        }
        expected_pairs: set[tuple[str, str, str]] = set()
        expected_count = 0
        for browser, variants in variants_by_browser.items():
            versions_by_os = resolved_versions.versions_for(browser)
            for variant in variants:
                version = versions_by_os.get(variant.os)
                if version is None:
                    continue
                expected_pairs.add((browser, variant.os, variant.platform))
                expected_count += len(version) if isinstance(version, list) else 1

        self.assertEqual(len(user_agents), expected_count)
        pairs = {(item["browser"], item["os"], item["platform"]) for item in user_agents}
        self.assertEqual(
            pairs,
            expected_pairs,
        )

        edge_windows = next(
            item for item in user_agents if item["browser"] == "edge" and item["os"] == "windows"
        )
        edge_windows_version = resolved_versions.versions_for("edge")["windows"]
        edge_windows_major = edge_windows_version.split(".", 1)[0]
        self.assertEqual(edge_windows["browser_major_version"], edge_windows_major)
        self.assertIn(f"Edg/{edge_windows_major}.0.0.0", edge_windows["user_agent"])


if __name__ == "__main__":
    unittest.main()
