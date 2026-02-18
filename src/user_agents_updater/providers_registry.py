from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .models import BrowserVersionsMap, JsonFetcher, MultiVersionsMap, RenderedUserAgentDTO, ScalarVersionsMap

ProviderSourceInfo = str | dict[str, str]
SourceByProviderMap = dict[str, ProviderSourceInfo]


class BrowserProvider(Protocol):
    name: str

    def source_urls(self) -> dict[str, str]:
        ...

    def fetch_versions(self, fetcher: JsonFetcher) -> tuple[BrowserVersionsMap, ProviderSourceInfo]:
        ...

    def build_user_agents(
        self, fetcher: JsonFetcher
    ) -> tuple[BrowserVersionsMap, list[RenderedUserAgentDTO], ProviderSourceInfo]:
        ...

    def render_user_agents(self, versions_by_os: BrowserVersionsMap) -> list[RenderedUserAgentDTO]:
        ...


class ProviderBase:
    def build_user_agents(
        self: BrowserProvider, fetcher: JsonFetcher
    ) -> tuple[BrowserVersionsMap, list[RenderedUserAgentDTO], ProviderSourceInfo]:
        versions, source = self.fetch_versions(fetcher)
        return versions, self.render_user_agents(versions), source


def single_source_url(endpoint: str) -> dict[str, str]:
    return {"default": endpoint}


def as_scalar_versions(versions_by_os: BrowserVersionsMap, browser: str) -> ScalarVersionsMap:
    resolved: ScalarVersionsMap = {}
    for os_name, value in versions_by_os.items():
        if not isinstance(value, str):
            raise RuntimeError(f"Invalid scalar version for browser '{browser}' and key '{os_name}'")
        resolved[os_name] = value
    return resolved


def as_multi_versions(versions_by_os: BrowserVersionsMap, browser: str) -> MultiVersionsMap:
    resolved: MultiVersionsMap = {}
    for os_name, value in versions_by_os.items():
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            raise RuntimeError(f"Invalid list version for browser '{browser}' and key '{os_name}'")
        resolved[os_name] = list(value)
    return resolved


@dataclass(frozen=True)
class ProviderRegistry:
    providers: dict[str, BrowserProvider]

    @classmethod
    def default(cls) -> ProviderRegistry:
        # Import local to avoid import cycles during module initialization.
        from .providers.chrome import ChromeProvider
        from .providers.edge import EdgeProvider
        from .providers.firefox import FirefoxProvider
        from .providers.safari import SafariProvider

        provider_instances: list[BrowserProvider] = [
            FirefoxProvider(),
            ChromeProvider(),
            EdgeProvider(),
            SafariProvider(),
        ]
        return cls(providers={provider.name: provider for provider in provider_instances})

    def all(self) -> list[BrowserProvider]:
        return list(self.providers.values())
