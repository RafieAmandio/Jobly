import logging

from bs4 import BeautifulSoup

from jobly.scrapers.base import JobFilters, JobResult
from jobly.scrapers.providers.direct import DirectScrapeProvider

logger = logging.getLogger(__name__)


class KarirProvider(DirectScrapeProvider):
    name = "karir"
    base_url = "https://www.karir.com"

    async def fetch_jobs(self, filters: JobFilters) -> list[JobResult]:
        client = self._get_client()
        query = " ".join(filters.keywords) if filters.keywords else ""

        try:
            response = await client.get(
                f"{self.base_url}/search",
                params={"q": query},
            )
            response.raise_for_status()
        except Exception:
            logger.exception("Karir.com: failed to fetch page")
            return []

        return self._parse_html(response.text)

    def _parse_html(self, html: str) -> list[JobResult]:
        soup = BeautifulSoup(html, "html.parser")
        results: list[JobResult] = []

        job_cards = soup.select("[class*='job-card'], [class*='JobCard'], .vacancy-card, article")
        for card in job_cards[:50]:
            try:
                title_el = card.select_one("h2, h3, [class*='title'], [class*='Title']")
                company_el = card.select_one("[class*='company'], [class*='Company']")
                location_el = card.select_one("[class*='location'], [class*='Location']")
                link_el = card.select_one("a[href]")

                title = title_el.get_text(strip=True) if title_el else None
                if not title:
                    continue

                url = ""
                if link_el and link_el.get("href"):
                    href = link_el["href"]
                    url = href if href.startswith("http") else f"{self.base_url}{href}"

                results.append(
                    JobResult(
                        external_id=f"karir-{hash(url)}",
                        source="karir",
                        title=title,
                        company=company_el.get_text(strip=True) if company_el else None,
                        location=location_el.get_text(strip=True) if location_el else None,
                        url=url,
                    )
                )
            except Exception:
                continue

        return results
