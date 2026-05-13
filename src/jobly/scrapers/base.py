from datetime import datetime
from typing import Protocol, runtime_checkable

from pydantic import BaseModel


class JobFilters(BaseModel):
    keywords: list[str] = []
    location: str | None = None
    country: str = "Indonesia"
    max_results: int = 50


class JobResult(BaseModel):
    external_id: str
    source: str
    title: str
    company: str | None = None
    description: str | None = None
    location: str | None = None
    url: str
    salary_min: int | None = None
    salary_max: int | None = None
    salary_text: str | None = None
    work_arrangement: str | None = None
    experience_level: str | None = None
    posted_at: datetime | None = None
    raw_data: dict | None = None


@runtime_checkable
class JobProvider(Protocol):
    name: str

    async def fetch_jobs(self, filters: JobFilters) -> list[JobResult]: ...

    async def health_check(self) -> bool: ...
