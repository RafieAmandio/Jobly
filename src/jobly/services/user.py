import secrets
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.models.reference import Category, Location, WorkArrangement
from jobly.models.user import User, UserCategory, UserLocation, UserPreference, UserWorkArrangement


def _generate_referral_code() -> str:
    return secrets.token_urlsafe(6).upper()[:8]


async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User | None:
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def create_user(
    session: AsyncSession,
    telegram_id: int,
    full_name: str,
    email: str | None = None,
    phone: str | None = None,
    language: str = "id",
    telegram_username: str | None = None,
) -> User:
    user = User(
        telegram_id=telegram_id,
        telegram_username=telegram_username,
        full_name=full_name,
        email=email,
        phone=phone,
        language=language,
        credit_balance=3,
        referral_code=_generate_referral_code(),
    )
    session.add(user)
    await session.flush()
    return user


async def save_preferences(
    session: AsyncSession,
    user: User,
    experience_level: str,
    salary_slug: str | None,
    category_indices: list[int],
    location_indices: list[int],
    arrangement_names: list[str],
) -> None:
    from jobly.constants.levels import SALARY_RANGES

    salary_min = None
    salary_max = None
    if salary_slug:
        for sr in SALARY_RANGES:
            if sr["slug"] == salary_slug:
                salary_min = sr["min"]
                salary_max = sr["max"]
                break

    pref = UserPreference(
        user_id=user.id,
        experience_level=experience_level,
        salary_min=salary_min,
        salary_max=salary_max,
        notification_language=user.language,
    )
    session.add(pref)

    from jobly.constants.categories import CATEGORIES
    from jobly.constants.locations import LOCATIONS

    cats = await session.execute(select(Category))
    all_cats = {c.slug: c.id for c in cats.scalars().all()}
    for idx in category_indices:
        slug = CATEGORIES[idx]["slug"]
        if slug in all_cats:
            session.add(UserCategory(user_id=user.id, category_id=all_cats[slug]))

    locs = await session.execute(select(Location))
    all_locs = {l.city: l.id for l in locs.scalars().all()}
    for idx in location_indices:
        city = LOCATIONS[idx]["city"]
        if city in all_locs:
            session.add(UserLocation(user_id=user.id, location_id=all_locs[city]))

    arrs = await session.execute(select(WorkArrangement))
    all_arrs = {a.name: a.id for a in arrs.scalars().all()}
    for name in arrangement_names:
        if name in all_arrs:
            session.add(UserWorkArrangement(user_id=user.id, arrangement_id=all_arrs[name]))

    user.onboarding_completed = True
    await session.flush()


async def update_language(session: AsyncSession, user: User, language: str) -> None:
    user.language = language
    await session.flush()


async def delete_user(session: AsyncSession, user: User) -> None:
    await session.delete(user)
    await session.flush()
