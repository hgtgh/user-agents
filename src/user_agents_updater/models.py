from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Callable
from typing import Literal

JsonFetcher = Callable[[str], tuple[str, object]]
PlatformName = Literal["desktop", "mobile"]
BrowserName = Literal["firefox", "chrome", "edge", "safari"]
VersionValue = str | list[str]
BrowserVersionsMap = dict[str, VersionValue]
ScalarVersionsMap = dict[str, str]
MultiVersionsMap = dict[str, list[str]]
FrozenVersionValue = str | tuple[str, ...]
FrozenVersionsMap = MappingProxyType[str, FrozenVersionValue]


@dataclass(frozen=True)
class RenderedUserAgentDTO:
    browser: BrowserName
    platform: PlatformName
    os: str
    browser_major_version: str
    user_agent: str

    def to_dict(self) -> dict[str, str]:
        return {
            "browser": self.browser,
            "platform": self.platform,
            "os": self.os,
            "browser_major_version": self.browser_major_version,
            "user_agent": self.user_agent,
        }


@dataclass(frozen=True)
class UARenderVariantDTO:
    platform: PlatformName
    os: str
    template: str
    token: str


@dataclass(frozen=True)
class ResolvedVersionsDTO:
    versions_by_browser: MappingProxyType[str, FrozenVersionsMap]

    @classmethod
    def from_mapping(cls, versions_by_browser: dict[str, BrowserVersionsMap]) -> "ResolvedVersionsDTO":
        if not versions_by_browser:
            raise RuntimeError("No browser versions provided")

        sanitized: dict[str, FrozenVersionsMap] = {}
        for browser, versions_by_os in versions_by_browser.items():
            sanitized[browser] = cls._sanitize_versions_map(versions_by_os, browser)

        return cls(versions_by_browser=MappingProxyType(sanitized))

    @staticmethod
    def _sanitize_versions_map(versions_by_os: BrowserVersionsMap, browser: str) -> FrozenVersionsMap:
        sanitized: dict[str, FrozenVersionValue] = {}
        for os_name, value in versions_by_os.items():
            if isinstance(value, str):
                sanitized[os_name] = value
                continue
            if isinstance(value, list) and all(isinstance(item, str) for item in value):
                sanitized[os_name] = tuple(value)
                continue
            raise RuntimeError(f"Invalid version value for browser '{browser}' and key '{os_name}'")
        return MappingProxyType(sanitized)

    def versions_for(self, browser: str) -> BrowserVersionsMap:
        versions_by_os = self.versions_by_browser.get(browser)
        if versions_by_os is None:
            raise RuntimeError(f"Missing versions for browser '{browser}'")
        return {
            os_name: list(value) if isinstance(value, tuple) else value
            for os_name, value in versions_by_os.items()
        }

    def to_dict(self) -> dict[str, BrowserVersionsMap]:
        return {
            browser: {
                os_name: list(value) if isinstance(value, tuple) else value
                for os_name, value in versions_by_os.items()
            }
            for browser, versions_by_os in self.versions_by_browser.items()
        }
