import unittest

from _fixtures import load_provider_fixture
from user_agents_updater.providers.safari import SafariProvider, extract_safari_stable_version  # noqa: E402


class SafariProviderTests(unittest.TestCase):
    def test_extract_safari_stable_version_ignores_beta(self):
        payload = load_provider_fixture("safari", "default")
        version = extract_safari_stable_version(payload)
        self.assertRegex(version, r"^\d+(?:\.\d+)*$")

    def test_extract_safari_stable_version_raises_without_stable_release(self):
        payload = {
            "interfaceLanguages": {
                "swift": [
                    {
                        "children": [
                            {"title": "Safari 26.3 Beta Release Notes", "type": "article"},
                            {"title": "Safari Technology Preview 999", "type": "article"},
                        ]
                    }
                ]
            },
        }
        with self.assertRaises(RuntimeError):
            extract_safari_stable_version(payload)

    def test_fetch_safari_versions_uses_provider_source(self):
        provider = SafariProvider()
        endpoint = provider.source_urls()["default"]

        def fake_fetcher(url):
            if url != endpoint:
                raise RuntimeError(f"unexpected URL: {url}")
            return url, load_provider_fixture(provider.name, "default")

        versions, source = provider.fetch_versions(fake_fetcher)
        self.assertEqual(source, endpoint)
        self.assertIn("macos", versions)
        self.assertIn("ios", versions)


if __name__ == "__main__":
    unittest.main()
