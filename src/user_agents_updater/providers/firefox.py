from __future__ import annotations

from ..models import BrowserVersionsMap, JsonFetcher, RenderedUserAgentDTO, ScalarVersionsMap, UARenderVariantDTO
from ..providers_registry import ProviderBase, ProviderSourceInfo, as_scalar_versions
from ..rendering import render_variants

FIREFOX_VARIANTS = [
    UARenderVariantDTO(
        platform="desktop",
        os="windows",
        token="Windows NT 10.0; Win64; x64",
        template="Mozilla/5.0 ({token}; rv:{major_version}.0) Gecko/20100101 Firefox/{major_version}.0",
    ),
    UARenderVariantDTO(
        platform="desktop",
        os="macos",
        token="Macintosh; Intel Mac OS X 10.15",
        template="Mozilla/5.0 ({token}; rv:{major_version}.0) Gecko/20100101 Firefox/{major_version}.0",
    ),
    UARenderVariantDTO(
        platform="desktop",
        os="linux",
        token="X11; Linux x86_64",
        template="Mozilla/5.0 ({token}; rv:{major_version}.0) Gecko/20100101 Firefox/{major_version}.0",
    ),
    UARenderVariantDTO(
        platform="desktop",
        os="ubuntu",
        token="X11; Ubuntu; Linux x86_64",
        template="Mozilla/5.0 ({token}; rv:{major_version}.0) Gecko/20100101 Firefox/{major_version}.0",
    ),
    # UARenderVariantDTO(
    #     platform="mobile",
    #     os="android",
    #     token="Android 10; Mobile",
    #     template="Mozilla/5.0 ({token}; rv:{major_version}.0) Gecko/{major_version}.0 Firefox/{major_version}.0",
    # ),
    # UARenderVariantDTO(
    #     platform="mobile",
    #     os="ios",
    #     token="iPhone; CPU iPhone OS 18_7 like Mac OS X",
    #     template="Mozilla/5.0 ({token}) AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/{major_version}.0 Mobile/15E148 Safari/604.1",
    # ),
]


def extract_firefox_release_version(data: object) -> str:
    if not isinstance(data, dict):
        raise RuntimeError("Unable to parse Firefox release version: data is not a dict")

    release_version = data.get("LATEST_FIREFOX_VERSION")
    if not isinstance(release_version, str) or not release_version.strip():
        raise RuntimeError("Unable to parse Firefox release version: missing 'LATEST_FIREFOX_VERSION'")
    return release_version


def extract_firefox_mobile_versions(data: object) -> tuple[str, str]:
    if not isinstance(data, dict):
        raise RuntimeError("Unable to parse Firefox mobile versions: data is not a dict")

    common_version = data.get("version")
    if not isinstance(common_version, str) or not common_version.strip():
        raise RuntimeError("Unable to parse Firefox mobile versions: missing 'version'")

    ios_value = data.get("ios_version")
    ios_version = ios_value if isinstance(ios_value, str) and ios_value.strip() else common_version
    return common_version, ios_version


class FirefoxProvider(ProviderBase):
    name = "firefox"
    desktop_endpoint = "https://product-details.mozilla.org/1.0/firefox_versions.json"
    mobile_endpoint = "https://product-details.mozilla.org/1.0/mobile_versions.json"

    def source_urls(self) -> dict[str, str]:
        return {
            "desktop": self.desktop_endpoint,
            "mobile": self.mobile_endpoint,
        }

    def fetch_versions(self, fetcher: JsonFetcher) -> tuple[ScalarVersionsMap, ProviderSourceInfo]:
        source_urls = self.source_urls()
        desktop_source, desktop_payload = fetcher(source_urls["desktop"])
        mobile_source, mobile_payload = fetcher(source_urls["mobile"])
        release_version = extract_firefox_release_version(desktop_payload)
        android_version, ios_version = extract_firefox_mobile_versions(mobile_payload)

        versions: ScalarVersionsMap = {
            "windows": release_version,
            "macos": release_version,
            "linux": release_version,
            "ubuntu": release_version,
            "android": android_version,
            "ios": ios_version,
        }
        sources = {
            "desktop": desktop_source,
            "mobile": mobile_source,
        }
        return versions, sources

    def render_user_agents(self, versions_by_os: BrowserVersionsMap) -> list[RenderedUserAgentDTO]:
        return render_variants(
            browser=self.name,
            variants=FIREFOX_VARIANTS,
            versions_by_os=as_scalar_versions(versions_by_os, self.name),
        )
