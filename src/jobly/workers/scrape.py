import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.db.session import async_session
from jobly.models.job import Job, JobCategory
from jobly.models.reference import Category
from jobly.scrapers.base import JobFilters, JobResult
from jobly.scrapers.dedup import compute_fingerprint, deduplicate_jobs
from jobly.scrapers.registry import registry
from jobly.services.ai import classify_job

logger = logging.getLogger(__name__)


async def run_scrape_cycle() -> list[Job]:
    filters = JobFilters(country="Indonesia", max_results=50)
    raw_jobs = await registry.fetch_all(filters)
    unique_jobs = deduplicate_jobs(raw_jobs)

    logger.info(f"Scraped {len(raw_jobs)} jobs, {len(unique_jobs)} unique after dedup")

    new_jobs: list[Job] = []
    async with async_session() as session:
        for job_result in unique_jobs:
            fingerprint = compute_fingerprint(job_result)

            existing = (
                await session.execute(
                    select(Job).where(Job.fingerprint == fingerprint)
                )
            ).scalar_one_or_none()

            if existing:
                continue

            job = Job(
                external_id=job_result.external_id,
                source=job_result.source,
                title=job_result.title,
                company=job_result.company,
                description=job_result.description,
                location=job_result.location,
                work_arrangement=job_result.work_arrangement,
                salary_min=job_result.salary_min,
                salary_max=job_result.salary_max,
                salary_text=job_result.salary_text,
                experience_level=job_result.experience_level,
                url=job_result.url,
                posted_at=job_result.posted_at,
                fingerprint=fingerprint,
                raw_data=job_result.raw_data,
            )
            session.add(job)
            await session.flush()

            if job_result.description:
                categories = await classify_job(job_result.title, job_result.description)
                all_cats = (await session.execute(select(Category))).scalars().all()
                cat_map = {c.slug: c.id for c in all_cats}

                for cat_data in categories:
                    slug = cat_data.get("slug", "")
                    if slug in cat_map:
                        session.add(
                            JobCategory(
                                job_id=job.id,
                                category_id=cat_map[slug],
                                confidence=cat_data.get("confidence", 1.0),
                            )
                        )

            new_jobs.append(job)

        await session.commit()

    logger.info(f"Stored {len(new_jobs)} new jobs")
    return new_jobs
