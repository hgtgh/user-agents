import unittest

from _fixtures import load_provider_fixture
from user_agents_updater.providers.firefox import (  # noqa: E402
    FirefoxProvider,
    extract_firefox_mobile_versions,
    extract_firefox_release_version,
)


class FirefoxProviderTests(unittest.TestCase):
    def test_extract_firefox_release_version(self):
        payload = load_provider_fixture("firefox", "desktop")
        self.assertEqual(
            extract_firefox_release_version(payload),
            payload["LATEST_FIREFOX_VERSION"],
        )

    def test_extract_firefox_mobile_versions(self):
        payload = load_provider_fixture("firefox", "mobile")
        android, ios = extract_firefox_mobile_versions(payload)
        self.assertEqual(android, payload["version"])
        self.assertEqual(ios, payload.get("ios_version") or payload["version"])

    def test_fetch_firefox_versions_uses_product_details_mobile_json(self):
        seen_urls: list[str] = []
        provider = FirefoxProvider()
        source_urls = provider.source_urls()
        desktop_url = source_urls["desktop"]
        mobile_url = source_urls["mobile"]

        def fake_fetcher(url):
            seen_urls.append(url)
            if url == desktop_url:
                return url, load_provider_fixture(provider.name, "desktop")
            if url == mobile_url:
                return url, load_provider_fixture(provider.name, "mobile")
            raise RuntimeError(f"unexpected URL: {url}")

        versions, sources = provider.fetch_versions(fetcher=fake_fetcher)
        desktop_payload = load_provider_fixture(provider.name, "desktop")
        mobile_payload = load_provider_fixture(provider.name, "mobile")
        expected_release = desktop_payload["LATEST_FIREFOX_VERSION"]
        expected_android = mobile_payload["version"]
        expected_ios = mobile_payload.get("ios_version") or expected_android
        self.assertEqual(
            seen_urls,
            [desktop_url, mobile_url],
        )
        self.assertEqual(versions["windows"], expected_release)
        self.assertEqual(versions["macos"], expected_release)
        self.assertEqual(versions["linux"], expected_release)
        self.assertEqual(versions["android"], expected_android)
        self.assertEqual(versions["ios"], expected_ios)
        self.assertEqual(sources["desktop"], desktop_url)
        self.assertEqual(sources["mobile"], mobile_url)

    def test_fetch_firefox_versions_uses_ios_version_when_present(self):
        def fake_fetcher(url):
            if url == "https://product-details.mozilla.org/1.0/firefox_versions.json":
                return url, {"LATEST_FIREFOX_VERSION": "147.0.3"}
            if url == "https://product-details.mozilla.org/1.0/mobile_versions.json":
                return url, {"version": "147.5", "ios_version": "147.7"}
            raise RuntimeError("unexpected URL")

        versions, _ = FirefoxProvider().fetch_versions(fetcher=fake_fetcher)
        self.assertEqual(versions["android"], "147.5")
        self.assertEqual(versions["ios"], "147.7")


if __name__ == "__main__":
    unittest.main()
