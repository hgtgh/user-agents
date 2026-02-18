from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from .models import BrowserVersionsMap, JsonFetcher, ResolvedVersionsDTO
from .providers_registry import ProviderRegistry, SourceByProviderMap


class UserAgentService:
    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self.registry = registry or ProviderRegistry.default()

    def generate(
        self,
        fetcher: JsonFetcher,
    ) -> tuple[ResolvedVersionsDTO, SourceByProviderMap, list[dict[str, str]]]:
        raw_versions: dict[str, BrowserVersionsMap] = {}
        sources: SourceByProviderMap = {}
        user_agents: list[dict[str, str]] = []
        providers = self.registry.all()

        with ThreadPoolExecutor(max_workers=len(providers)) as executor:
            future_by_provider = {
                executor.submit(provider.build_user_agents, fetcher): provider for provider in providers
            }
            for future, provider in future_by_provider.items():
                versions, rendered_user_agents, source = future.result()
                raw_versions[provider.name] = versions
                user_agents.extend(rendered.to_dict() for rendered in rendered_user_agents)
                sources[provider.name] = source

        return ResolvedVersionsDTO.from_mapping(raw_versions), sources, user_agents
