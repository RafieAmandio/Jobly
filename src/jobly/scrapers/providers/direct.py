import logging
from abc import ABC, abstractmethod

import httpx

from jobly.scrapers.base import JobFilters, JobResult

logger = logging.getLogger(__name__)


class DirectScrapeProvider(ABC):
    name: str
    base_url: str

    def __init__(self) -> None:
        self._client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                timeout=30,
                headers={
                    "User-Agent": (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
                },
            )
        return self._client

    @abstractmethod
    async def fetch_jobs(self, filters: JobFilters) -> list[JobResult]: ...

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            response = await client.get(self.base_url)
            return response.status_code == 200
        except Exception:
            return False

    async def close(self) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None
