from jobly.config import settings
from jobly.scrapers.providers.apify import ApifyProvider
from jobly.scrapers.registry import registry


def register_providers() -> None:
    if not settings.apify.api_token:
        return

    for source in ("linkedin", "indeed", "glassdoor", "jobstreet"):
        registry.register(ApifyProvider(source))
