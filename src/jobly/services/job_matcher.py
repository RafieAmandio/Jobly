import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.models.job import Job, JobCategory
from jobly.models.notification import NotificationLog
from jobly.models.reference import Category, Location
from jobly.models.user import User, UserCategory, UserLocation

logger = logging.getLogger(__name__)


async def find_matching_users(session: AsyncSession, job: Job) -> list[User]:
    job_cat_ids = [jc.category_id for jc in job.categories]
    if not job_cat_ids:
        return []

    matching_user_ids_q = (
        select(UserCategory.user_id)
        .where(UserCategory.category_id.in_(job_cat_ids))
        .distinct()
    )
    matching_user_ids = (await session.execute(matching_user_ids_q)).scalars().all()
    if not matching_user_ids:
        return []

    already_notified_q = (
        select(NotificationLog.user_id)
        .where(
            NotificationLog.job_id == job.id,
            NotificationLog.user_id.in_(matching_user_ids),
        )
    )
    already_notified = set((await session.execute(already_notified_q)).scalars().all())

    user_ids_to_notify = [uid for uid in matching_user_ids if uid not in already_notified]
    if not user_ids_to_notify:
        return []

    users_q = select(User).where(
        User.id.in_(user_ids_to_notify),
        User.is_active == True,
        User.onboarding_completed == True,
    )
    users = (await session.execute(users_q)).scalars().all()
    return list(users)


async def match_job_location(session: AsyncSession, user: User, job: Job) -> bool:
    user_loc_ids = (
        await session.execute(
            select(UserLocation.location_id).where(UserLocation.user_id == user.id)
        )
    ).scalars().all()

    if not user_loc_ids:
        return True

    user_locs = (
        await session.execute(select(Location).where(Location.id.in_(user_loc_ids)))
    ).scalars().all()

    for loc in user_locs:
        if loc.city == "Remote / Anywhere":
            return True
        if job.location and loc.city.lower() in job.location.lower():
            return True

    return False
