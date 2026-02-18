from __future__ import annotations

from ..config import CHROMIUM_TOKENS
from ..models import BrowserVersionsMap, JsonFetcher, RenderedUserAgentDTO, ScalarVersionsMap, UARenderVariantDTO
from ..providers_registry import ProviderBase, ProviderSourceInfo, single_source_url
from ..rendering import render_variants

EDGE_VARIANTS = [
    UARenderVariantDTO(
        platform="desktop",
        os="windows",
        token=CHROMIUM_TOKENS["windows"],
        template="Mozilla/5.0 ({token}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36 Edg/{major_version}.0.0.0",
    ),
    # UARenderVariantDTO(
    #     platform="desktop",
    #     os="macos",
    #     token=CHROMIUM_TOKENS["macos"],
    #     template="Mozilla/5.0 ({token}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36 Edg/{major_version}.0.0.0",
    # ),

    # TODO: Mobile devices require the OS version.
    # UARenderVariantDTO(
    #     platform="mobile",
    #     os="android",
    #     token=CHROMIUM_TOKENS["android"],
    #     template="Mozilla/5.0 ({token}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36 EdgA/{version}",
    # ),
    # UARenderVariantDTO(
    #     platform="mobile",
    #     os="ios",
    #     token=CHROMIUM_TOKENS["ios"],
    #     template="Mozilla/5.0 ({token}) AppleWebKit/605.1.15 (KHTML, like Gecko) EdgiOS/{version} Version/26.0 Mobile/15E148 Safari/604.1",
    # ),
]


def extract_edge_versions(data: object) -> ScalarVersionsMap:
    try:
        releases = next(r for r in data if r["Product"] == "Stable")["Releases"]
        versions: ScalarVersionsMap = {}
        for release in releases:
            os_name = release["Platform"].lower()
            if os_name == "windows" and release.get("Architecture") != "x64":
                continue
            if os_name not in versions:
                versions[os_name] = release["ProductVersion"]
        return versions
    except (StopIteration, KeyError, TypeError) as err:
        raise RuntimeError("Unable to parse Edge stable versions payload") from err


class EdgeProvider(ProviderBase):
    name = "edge"
    endpoint = "https://edgeupdates.microsoft.com/api/products"

    def source_urls(self) -> dict[str, str]:
        return single_source_url(self.endpoint)

    def fetch_versions(self, fetcher: JsonFetcher) -> tuple[ScalarVersionsMap, ProviderSourceInfo]:
        source, payload = fetcher(self.source_urls()["default"])
        return extract_edge_versions(payload), source

    def render_user_agents(self, versions_by_os: BrowserVersionsMap) -> list[RenderedUserAgentDTO]:
        return render_variants(
            browser=self.name,
            variants=EDGE_VARIANTS,
            versions_by_os=versions_by_os,
        )
