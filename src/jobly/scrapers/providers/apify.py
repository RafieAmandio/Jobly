import logging
from datetime import datetime

from apify_client import ApifyClientAsync

from jobly.config import settings
from jobly.scrapers.base import JobFilters, JobResult

logger = logging.getLogger(__name__)

ACTOR_MAP = {
    "linkedin": "curious_coder/linkedin-jobs-scraper",
    "indeed": "misceres/indeed-scraper",
}


class ApifyProvider:
    def __init__(self, source: str, actor_id: str | None = None) -> None:
        self.name = source
        self.actor_id = actor_id or ACTOR_MAP.get(source, "")
        self._client: ApifyClientAsync | None = None

    def _get_client(self) -> ApifyClientAsync:
        if self._client is None:
            self._client = ApifyClientAsync(token=settings.apify.api_token)
        return self._client

    async def fetch_jobs(self, filters: JobFilters) -> list[JobResult]:
        client = self._get_client()

        run_input = self._build_input(filters)
        if not run_input:
            return []

        try:
            run = await client.actor(self.actor_id).call(run_input=run_input)
            dataset = client.dataset(run["defaultDatasetId"])
            items = []
            async for item in dataset.iterate_items():
                items.append(item)

            results = [self._parse_item(item) for item in items]
            return [r for r in results if r is not None]
        except Exception:
            logger.exception(f"Apify {self.name}: failed to run actor {self.actor_id}")
            return []

    def _build_input(self, filters: JobFilters) -> dict | None:
        if self.name == "linkedin":
            query = "+".join(filters.keywords) if filters.keywords else "software+engineer"
            location = filters.location or "Indonesia"
            url = f"https://www.linkedin.com/jobs/search/?keywords={query}&location={location}"
            return {
                "urls": [url],
                "count": filters.max_results,
                "scrapeCompany": False,
            }
        elif self.name == "indeed":
            position = " ".join(filters.keywords) if filters.keywords else ""
            return {
                "position": position,
                "country": "ID",
                "location": filters.location or "Indonesia",
                "maxItems": filters.max_results,
                "saveOnlyUniqueItems": True,
            }
        return None

    def _parse_item(self, item: dict) -> JobResult | None:
        try:
            title = item.get("title") or item.get("jobTitle") or item.get("positionName") or item.get("name", "")
            if not title:
                return None

            url = (
                item.get("url")
                or item.get("link")
                or item.get("jobUrl")
                or item.get("applyUrl", "")
            )

            posted_str = item.get("postedAt") or item.get("date") or item.get("postedDate") or item.get("postedTime")
            posted_at = None
            if posted_str:
                try:
                    posted_at = datetime.fromisoformat(posted_str.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass

            return JobResult(
                external_id=str(item.get("id") or item.get("jobId") or hash(url)),
                source=self.name,
                title=title,
                company=item.get("company") or item.get("companyName") or item.get("employer"),
                description=item.get("description") or item.get("jobDescription"),
                location=item.get("location") or item.get("jobLocation"),
                url=url,
                salary_text=item.get("salary") or item.get("salaryRange"),
                work_arrangement=item.get("workType") or item.get("employmentType"),
                posted_at=posted_at,
                raw_data=item,
            )
        except Exception:
            logger.exception(f"Failed to parse {self.name} item")
            return None

    async def health_check(self) -> bool:
        try:
            client = self._get_client()
            user = await client.user().get()
            return user is not None
        except Exception:
            return False
