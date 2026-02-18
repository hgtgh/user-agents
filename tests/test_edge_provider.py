import unittest

from _fixtures import load_provider_fixture
from user_agents_updater.providers.edge import EdgeProvider, extract_edge_versions  # noqa: E402


class EdgeProviderTests(unittest.TestCase):
    def test_extract_edge_versions_all_platforms(self):
        payload = load_provider_fixture("edge", "default")
        versions = extract_edge_versions(payload)
        self.assertIn("windows", versions)
        self.assertTrue(versions["windows"])
        self.assertTrue(any(key in versions for key in ("macos", "linux", "android", "ios")))

    def test_fetch_edge_versions_uses_provider_source(self):
        provider = EdgeProvider()
        endpoint = provider.source_urls()["default"]

        def fake_fetcher(url):
            if url != endpoint:
                raise RuntimeError(f"unexpected URL: {url}")
            return url, load_provider_fixture(provider.name, "default")

        versions, source = provider.fetch_versions(fake_fetcher)
        self.assertEqual(source, endpoint)
        self.assertEqual(versions, extract_edge_versions(load_provider_fixture(provider.name, "default")))


if __name__ == "__main__":
    unittest.main()
