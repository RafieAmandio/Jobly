import pytest

from jobly.scrapers.base import JobFilters
from jobly.scrapers.providers.apify import ApifyProvider


@pytest.mark.integration
@pytest.mark.asyncio
async def test_apify_health_check():
    provider = ApifyProvider(source="linkedin")
    is_healthy = await provider.health_check()
    assert is_healthy is True
