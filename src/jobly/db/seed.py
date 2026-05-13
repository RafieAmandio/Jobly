import logging

from sqlalchemy import select

from jobly.constants.categories import CATEGORIES
from jobly.constants.levels import WORK_ARRANGEMENTS
from jobly.constants.locations import LOCATIONS
from jobly.db.session import async_session
from jobly.models.reference import Category, Location, WorkArrangement

logger = logging.getLogger(__name__)


async def seed_reference_data() -> None:
    async with async_session() as session:
        existing_cats = (await session.execute(select(Category))).scalars().all()
        if not existing_cats:
            for cat_data in CATEGORIES:
                session.add(Category(**cat_data))
            logger.info(f"Seeded {len(CATEGORIES)} categories")

        existing_locs = (await session.execute(select(Location))).scalars().all()
        if not existing_locs:
            for loc_data in LOCATIONS:
                session.add(Location(**loc_data))
            logger.info(f"Seeded {len(LOCATIONS)} locations")

        existing_arrs = (await session.execute(select(WorkArrangement))).scalars().all()
        if not existing_arrs:
            for arr_data in WORK_ARRANGEMENTS:
                session.add(WorkArrangement(**arr_data))
            logger.info(f"Seeded {len(WORK_ARRANGEMENTS)} work arrangements")

        await session.commit()
