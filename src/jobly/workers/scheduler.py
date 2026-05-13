import logging

from aiogram import Bot

logger = logging.getLogger(__name__)

_bot_instance: Bot | None = None


def set_bot(bot: Bot) -> None:
    global _bot_instance
    _bot_instance = bot


async def hourly_scrape_job() -> None:
    from jobly.workers.notify import notify_users_for_jobs
    from jobly.workers.scrape import run_scrape_cycle

    logger.info("Starting hourly scrape cycle")
    new_jobs = await run_scrape_cycle()
    if new_jobs and _bot_instance:
        await notify_users_for_jobs(_bot_instance, new_jobs)
    logger.info(f"Hourly scrape complete: {len(new_jobs)} new jobs")
