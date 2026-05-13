from unittest.mock import AsyncMock

import pytest

from jobly.scrapers.base import JobFilters, JobResult
from jobly.scrapers.registry import ProviderRegistry


class MockProvider:
    def __init__(self, name: str, jobs: list[JobResult] | None = None):
        self.name = name
        self._jobs = jobs or []

    async def fetch_jobs(self, filters: JobFilters) -> list[JobResult]:
        return self._jobs

    async def health_check(self) -> bool:
        return True


class FailingProvider:
    name = "failing"

    async def fetch_jobs(self, filters: JobFilters) -> list[JobResult]:
        raise RuntimeError("Scraper error")

    async def health_check(self) -> bool:
        return False


@pytest.mark.asyncio
async def test_registry_register_and_fetch():
    reg = ProviderRegistry()
    job = JobResult(
        external_id="1", source="test", title="Engineer", url="https://example.com"
    )
    reg.register(MockProvider("test", [job]))

    results = await reg.fetch_all(JobFilters())
    assert len(results) == 1
    assert results[0].title == "Engineer"


@pytest.mark.asyncio
async def test_registry_multiple_providers():
    reg = ProviderRegistry()
    job1 = JobResult(external_id="1", source="a", title="Job A", url="https://a.com")
    job2 = JobResult(external_id="2", source="b", title="Job B", url="https://b.com")
    reg.register(MockProvider("a", [job1]))
    reg.register(MockProvider("b", [job2]))

    results = await reg.fetch_all(JobFilters())
    assert len(results) == 2


@pytest.mark.asyncio
async def test_registry_failing_provider_doesnt_block():
    reg = ProviderRegistry()
    job = JobResult(external_id="1", source="good", title="Good Job", url="https://good.com")
    reg.register(FailingProvider())
    reg.register(MockProvider("good", [job]))

    results = await reg.fetch_all(JobFilters())
    assert len(results) == 1


@pytest.mark.asyncio
async def test_registry_health_check():
    reg = ProviderRegistry()
    reg.register(MockProvider("healthy"))
    reg.register(FailingProvider())

    statuses = await reg.health_check_all()
    assert statuses["healthy"] is True
    assert statuses["failing"] is False


@pytest.mark.asyncio
async def test_registry_unregister():
    reg = ProviderRegistry()
    reg.register(MockProvider("test"))
    assert reg.get("test") is not None
    reg.unregister("test")
    assert reg.get("test") is None
