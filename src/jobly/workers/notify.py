import logging

from aiogram import Bot

from jobly.db.session import async_session
from jobly.models.job import Job
from jobly.services.job_matcher import find_matching_users, match_job_location
from jobly.services.notification import send_job_notification

logger = logging.getLogger(__name__)

MAX_NOTIFICATIONS_PER_USER_PER_HOUR = 10


async def notify_users_for_jobs(bot: Bot, jobs: list[Job]) -> int:
    total_sent = 0

    async with async_session() as session:
        for job in jobs:
            job_in_session = await session.merge(job)
            matching_users = await find_matching_users(session, job_in_session)

            for user in matching_users:
                if not await match_job_location(session, user, job_in_session):
                    continue

                success = await send_job_notification(bot, session, user, job_in_session)
                if success:
                    total_sent += 1

        await session.commit()

    logger.info(f"Sent {total_sent} job notifications")
    return total_sent
