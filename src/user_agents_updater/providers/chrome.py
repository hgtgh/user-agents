from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from ..config import CHROMIUM_TOKENS
from ..models import BrowserVersionsMap, JsonFetcher, MultiVersionsMap, RenderedUserAgentDTO, UARenderVariantDTO
from ..parsers import parse_semver_like
from ..providers_registry import ProviderBase, ProviderSourceInfo
from ..rendering import render_variants

CHROME_DEFAULT_MAJOR_COUNT = 3
CHROME_VARIANTS = [
    UARenderVariantDTO(
        platform="desktop",
        os="windows",
        token=CHROMIUM_TOKENS["windows"],
        template="Mozilla/5.0 ({token}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36",
    ),
    UARenderVariantDTO(
        platform="desktop",
        os="macos",
        token=CHROMIUM_TOKENS["macos"],
        template="Mozilla/5.0 ({token}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36",
    ),
    UARenderVariantDTO(
        platform="desktop",
        os="linux",
        token=CHROMIUM_TOKENS["linux"],
        template="Mozilla/5.0 ({token}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{major_version}.0.0.0 Safari/537.36",
    ),

    # TODO: Mobile devices require the OS version.
    # UARenderVariantDTO(
    #     platform="mobile",
    #     os="android",
    #     token=CHROMIUM_TOKENS["android"],
    #     template="Mozilla/5.0 ({token}) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version} Mobile Safari/537.36",
    # ),
    # UARenderVariantDTO(
    #     platform="mobile",
    #     os="ios",
    #     token=CHROMIUM_TOKENS["ios"], # requires iOS version
    #     template="Mozilla/5.0 ({token}) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{version} Mobile/15E148 Safari/604.1",
    # ),
]


def _extract_chrome_versionhistory_candidates(data: object) -> list[str]:
    if not isinstance(data, dict):
        raise RuntimeError("Invalid VersionHistory payload")
    versions = data.get("versions")
    if not isinstance(versions, list):
        raise RuntimeError("Missing versions list in VersionHistory payload")

    candidates: list[str] = []
    for item in versions:
        if not isinstance(item, dict):
            continue
        value = item.get("version")
        if isinstance(value, str):
            candidates.append(value)

    if not candidates:
        raise RuntimeError("No Chrome versions found in VersionHistory payload")

    return candidates


def extract_chrome_latest_major_versions(
    data: object,
    major_count: int = CHROME_DEFAULT_MAJOR_COUNT,
) -> list[str]:
    if major_count < 1:
        raise RuntimeError("major_count must be >= 1")

    major_versions: list[str] = []
    seen: set[int] = set()
    for version in sorted(_extract_chrome_versionhistory_candidates(data), key=parse_semver_like, reverse=True):
        parsed = parse_semver_like(version)
        if not parsed:
            continue
        major = parsed[0]
        if major in seen:
            continue
        seen.add(major)
        major_versions.append(version)
        if len(major_versions) == major_count:
            return major_versions

    if not major_versions:
        raise RuntimeError("No parseable Chrome semantic versions found in VersionHistory payload")

    return major_versions


def _resolve_chrome_source(
    source_key: str,
    url: str,
    fetcher: JsonFetcher,
    major_count: int,
) -> tuple[str, list[str], str]:
    source, payload = fetcher(url)
    return source_key, extract_chrome_latest_major_versions(payload, major_count), source


@dataclass(frozen=True)
class ChromeProvider(ProviderBase):
    major_count: int = CHROME_DEFAULT_MAJOR_COUNT
    name = "chrome"
    versionhistory_url_template = (
        "https://versionhistory.googleapis.com/v1/chrome/platforms/{platform}/"
        "channels/stable/versions?order_by=version%20desc&pageSize=30"
    )
    platform_segments = {
        "windows": "win64",
        "macos": "mac",
        "linux": "linux",
        "android": "android",
        "ios": "ios",
    }

    def source_urls(self) -> dict[str, str]:
        return {
            os_name: self.versionhistory_url_template.format(platform=platform_segment)
            for os_name, platform_segment in self.platform_segments.items()
        }

    def fetch_versions(self, fetcher: JsonFetcher) -> tuple[MultiVersionsMap, ProviderSourceInfo]:
        if self.major_count < 1:
            raise RuntimeError("major_count must be >= 1")

        versions: MultiVersionsMap = {}
        sources: dict[str, str] = {}
        source_urls = self.source_urls()

        with ThreadPoolExecutor(max_workers=len(source_urls)) as executor:
            futures = [
                executor.submit(
                    _resolve_chrome_source,
                    source_key,
                    url,
                    fetcher,
                    self.major_count,
                )
                for source_key, url in source_urls.items()
            ]
            for future in futures:
                source_key, version, source = future.result()
                versions[source_key] = version
                sources[source_key] = source

        return versions, sources

    def render_user_agents(self, versions_by_os: BrowserVersionsMap) -> list[RenderedUserAgentDTO]:
        return render_variants(
            browser=self.name,
            variants=CHROME_VARIANTS,
            versions_by_os=versions_by_os,
        )
