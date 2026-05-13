import logging

from jobly.scrapers.base import JobFilters, JobProvider, JobResult

logger = logging.getLogger(__name__)


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: dict[str, JobProvider] = {}

    def register(self, provider: JobProvider) -> None:
        self._providers[provider.name] = provider
        logger.info(f"Registered job provider: {provider.name}")

    def unregister(self, name: str) -> None:
        self._providers.pop(name, None)

    def get(self, name: str) -> JobProvider | None:
        return self._providers.get(name)

    @property
    def all_providers(self) -> list[JobProvider]:
        return list(self._providers.values())

    async def fetch_all(self, filters: JobFilters) -> list[JobResult]:
        all_results: list[JobResult] = []
        for provider in self._providers.values():
            try:
                results = await provider.fetch_jobs(filters)
                all_results.extend(results)
                logger.info(f"{provider.name}: fetched {len(results)} jobs")
            except Exception:
                logger.exception(f"{provider.name}: failed to fetch jobs")
        return all_results

    async def health_check_all(self) -> dict[str, bool]:
        statuses: dict[str, bool] = {}
        for name, provider in self._providers.items():
            try:
                statuses[name] = await provider.health_check()
            except Exception:
                statuses[name] = False
        return statuses


registry = ProviderRegistry()
