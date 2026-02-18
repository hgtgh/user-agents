from .providers.chrome import (
    extract_chrome_latest_major_versions,
    ChromeProvider,
)
from .providers.edge import EdgeProvider
from .providers.firefox import extract_firefox_release_version, FirefoxProvider
from .http import fetch_json
from .models import RenderedUserAgentDTO, ResolvedVersionsDTO
from .providers_registry import ProviderRegistry
from .providers.safari import extract_safari_stable_version, SafariProvider
from .service import UserAgentService

__all__ = [
    "fetch_json",
    "FirefoxProvider",
    "ChromeProvider",
    "EdgeProvider",
    "SafariProvider",
    "extract_firefox_release_version",
    "extract_chrome_latest_major_versions",
    "extract_safari_stable_version",
    "ProviderRegistry",
    "UserAgentService",
    "RenderedUserAgentDTO",
    "ResolvedVersionsDTO",
]
