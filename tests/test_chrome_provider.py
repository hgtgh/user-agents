import unittest

from _fixtures import load_provider_fixture
from user_agents_updater.providers.chrome import (  # noqa: E402
    ChromeProvider,
    extract_chrome_latest_major_versions,
)


class ChromeProviderTests(unittest.TestCase):
    def test_extract_chrome_latest_major_versions(self):
        payload = load_provider_fixture("chrome", "windows")
        major_count = ChromeProvider().major_count
        expected_latest_majors: list[str] = []
        seen_majors: set[str] = set()
        for item in payload["versions"]:
            version = item["version"]
            major = version.split(".", 1)[0]
            if major in seen_majors:
                continue
            seen_majors.add(major)
            expected_latest_majors.append(version)
            if len(expected_latest_majors) == major_count:
                break

        self.assertEqual(
            extract_chrome_latest_major_versions(payload, major_count=major_count),
            expected_latest_majors,
        )

    def test_fetch_chrome_versions_uses_versionhistory_only(self):
        provider = ChromeProvider()
        fixtures_by_url = {
            url: load_provider_fixture(provider.name, source_key)
            for source_key, url in provider.source_urls().items()
        }

        def fake_fetcher(url):
            return url, fixtures_by_url[url]

        versions, sources = provider.fetch_versions(fetcher=fake_fetcher)
        self.assertEqual(set(versions.keys()), set(provider.source_urls().keys()))
        for source_key, items in versions.items():
            fixture_payload = fixtures_by_url[provider.source_urls()[source_key]]
            seen_majors: set[str] = set()
            for item in fixture_payload["versions"]:
                seen_majors.add(item["version"].split(".", 1)[0])
                if len(seen_majors) == provider.major_count:
                    break
            self.assertEqual(len(items), len(seen_majors))
            self.assertEqual(len(items), len({version.split(".", 1)[0] for version in items}))
        self.assertEqual(sources["macos"], provider.source_urls()["macos"])

    def test_fetch_chrome_versions_with_custom_major_count(self):
        provider = ChromeProvider(major_count=3)
        fixtures_by_url = {
            url: load_provider_fixture(provider.name, source_key)
            for source_key, url in provider.source_urls().items()
        }

        def fake_fetcher(url):
            return url, fixtures_by_url[url]

        versions, _ = provider.fetch_versions(fetcher=fake_fetcher)
        self.assertEqual(len(versions["windows"]), 3)

    def test_extract_chrome_latest_major_versions_rejects_invalid_major_count(self):
        with self.assertRaises(RuntimeError):
            extract_chrome_latest_major_versions({"versions": [{"version": "145.0.7632.46"}]}, 0)

    def test_extract_chrome_latest_major_versions_returns_available_majors_when_fewer_than_requested(self):
        payload = {
            "versions": [
                {"version": "145.0.7632.46"},
                {"version": "145.0.7632.45"},
                {"version": "144.0.7559.132"},
                {"version": "143.0.7499.40"},
            ]
        }
        self.assertEqual(
            extract_chrome_latest_major_versions(payload, major_count=4),
            ["145.0.7632.46", "144.0.7559.132", "143.0.7499.40"],
        )


if __name__ == "__main__":
    unittest.main()
