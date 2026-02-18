from __future__ import annotations

from collections.abc import Mapping

from .models import BrowserName, RenderedUserAgentDTO, UARenderVariantDTO, VersionValue
from .parsers import major_version


def render_variants(
    browser: BrowserName,
    variants: list[UARenderVariantDTO],
    versions_by_os: Mapping[str, VersionValue],
) -> list[RenderedUserAgentDTO]:
    """
    Render a list of variants into user-agents.

    - versions_by_os[os] can contain:
        - a single version (str)  -> 1 UA per variant
        - multiple versions (list[str]) -> N UAs per variant
    """
    rendered: list[RenderedUserAgentDTO] = []

    for variant in variants:
        versions = versions_by_os[variant.os]
        versions_list = [versions] if isinstance(versions, str) else versions

        rendered.extend(
            _render_variant(browser=browser, variant=variant, version=version)
            for version in versions_list
        )

    return rendered


def _render_variant(
    browser: BrowserName,
    variant: UARenderVariantDTO,
    version: str,
) -> RenderedUserAgentDTO:
    major = major_version(version)
    return RenderedUserAgentDTO(
        browser=browser,
        platform=variant.platform,
        os=variant.os,
        browser_major_version=major,
        user_agent=variant.template.format(
            token=variant.token,
            version=version,
            major_version=major,
        ),
    )
