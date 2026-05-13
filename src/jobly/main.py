import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from jobly.config import settings

logger = logging.getLogger(__name__)


def setup_logging() -> None:
    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def create_bot() -> Bot:
    return Bot(
        token=settings.telegram.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    redis = Redis.from_url(settings.redis.url)
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    from jobly.bot.middlewares.auth import AuthMiddleware
    from jobly.bot.middlewares.db import DbSessionMiddleware
    from jobly.bot.middlewares.i18n import I18nMiddleware

    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.outer_middleware(AuthMiddleware())
    dp.update.outer_middleware(I18nMiddleware())

    from jobly.bot.handlers import credits, cv, profile, start, tailor

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(credits.router)
    dp.include_router(cv.router)
    dp.include_router(tailor.router)

    return dp


async def on_startup(bot: Bot) -> None:
    from jobly.db.seed import seed_reference_data

    await seed_reference_data()

    _setup_scheduler(bot)

    logger.info("Bot started successfully")


def _setup_scheduler(bot: Bot) -> None:
    try:
        from apscheduler import AsyncScheduler
        from apscheduler.triggers.interval import IntervalTrigger

        scheduler = AsyncScheduler()

        async def hourly_scrape_job() -> None:
            from jobly.workers.scrape import run_scrape_cycle
            from jobly.workers.notify import notify_users_for_jobs

            new_jobs = await run_scrape_cycle()
            if new_jobs:
                await notify_users_for_jobs(bot, new_jobs)

        asyncio.get_event_loop().create_task(_start_scheduler(scheduler, hourly_scrape_job))
    except ImportError:
        logger.warning("APScheduler not available, skipping scheduled tasks")


async def _start_scheduler(scheduler, job_func) -> None:
    from apscheduler.triggers.interval import IntervalTrigger

    async with scheduler:
        await scheduler.add_schedule(
            job_func,
            IntervalTrigger(hours=1),
            id="hourly_scrape",
        )
        await scheduler.run_until_stopped()


async def start_polling() -> None:
    setup_logging()
    bot = create_bot()
    dp = create_dispatcher()
    dp.startup.register(on_startup)

    logger.info("Starting bot in polling mode...")
    await dp.start_polling(bot)


async def start_webhook() -> None:
    from aiohttp import web
    from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application

    setup_logging()
    bot = create_bot()
    dp = create_dispatcher()
    dp.startup.register(on_startup)

    async def on_startup_webhook(bot: Bot) -> None:
        await bot.set_webhook(
            url=f"{settings.telegram.webhook_url}/webhook",
            secret_token=settings.telegram.webhook_secret,
        )

    dp.startup.register(on_startup_webhook)

    app = web.Application()

    webhook_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
        secret_token=settings.telegram.webhook_secret,
    )
    webhook_handler.register(app, path="/webhook")

    from jobly.web.routes import setup_routes

    setup_routes(app)

    setup_application(app, dp, bot=bot)
    web.run_app(app, host="0.0.0.0", port=8080)


def main() -> None:
    if settings.is_production:
        asyncio.run(start_webhook())
    else:
        asyncio.run(start_polling())


if __name__ == "__main__":
    main()
