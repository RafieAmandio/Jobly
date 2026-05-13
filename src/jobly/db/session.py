from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from jobly.config import settings

engine = create_async_engine(
    settings.database.url,
    echo=settings.app_env == "development",
    pool_size=20,
    max_overflow=10,
)

async_session = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_session() -> AsyncSession:
    async with async_session() as session:
        yield session
