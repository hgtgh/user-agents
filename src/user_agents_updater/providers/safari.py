from __future__ import annotations

import re

from ..models import BrowserVersionsMap, JsonFetcher, RenderedUserAgentDTO, ScalarVersionsMap, UARenderVariantDTO
from ..parsers import parse_semver_like
from ..providers_registry import (
    ProviderBase,
    ProviderSourceInfo,
    as_scalar_versions,
    single_source_url,
)
from ..rendering import render_variants

SAFARI_VARIANTS = [
    UARenderVariantDTO(
        platform="desktop",
        os="macos",
        token="Macintosh; Intel Mac OS X 10_15_7",
        template="Mozilla/5.0 ({token}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Safari/605.1.15",
    ),
    # UARenderVariantDTO(
    #     platform="mobile",
    #     os="ios",
    #     token="iPhone; CPU iPhone OS 18_7 like Mac OS X",
    #     template="Mozilla/5.0 ({token}) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{version} Mobile/15E148 Safari/604.1",
    # ),
]


def extract_safari_stable_version(data: dict) -> str:
    children = (
        data.get("interfaceLanguages", {})
        .get("swift", [{}])[0]
        .get("children", [])
    )
    if not isinstance(children, list):
        raise RuntimeError("Unable to parse Safari stable version")

    candidates: set[str] = set()
    for child in children:
        if not isinstance(child, dict):
            continue
        if child.get("type") != "article":
            continue
        title = child.get("title")
        if not isinstance(title, str):
            continue
        if re.search(r"\bbeta\b", title, flags=re.IGNORECASE):
            continue
        match = re.search(r"\bSafari\s+(\d+(?:\.\d+)*)\s+Release Notes\b", title)
        if match:
            candidates.add(match.group(1))

    if not candidates:
        raise RuntimeError("Unable to parse Safari stable version")

    return max(candidates, key=parse_semver_like)


class SafariProvider(ProviderBase):
    name = "safari"
    endpoint = "https://developer.apple.com/tutorials/data/index/safari-release-notes"

    def source_urls(self) -> dict[str, str]:
        return single_source_url(self.endpoint)

    def fetch_versions(self, fetcher: JsonFetcher) -> tuple[ScalarVersionsMap, ProviderSourceInfo]:
        source, payload = fetcher(self.source_urls()["default"])
        version = extract_safari_stable_version(payload)
        versions: ScalarVersionsMap = {"macos": version, "ios": version}
        return versions, source

    def render_user_agents(self, versions_by_os: BrowserVersionsMap) -> list[RenderedUserAgentDTO]:
        return render_variants(
            browser=self.name,
            variants=SAFARI_VARIANTS,
            versions_by_os=as_scalar_versions(versions_by_os, self.name),
        )
