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
    import structlog

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if not settings.is_production else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(logging, settings.log_level.upper(), logging.INFO)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        level=getattr(logging, settings.log_level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    if settings.sentry_dsn:
        import sentry_sdk

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            traces_sample_rate=0.1,
            environment=settings.app_env,
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
    from jobly.bot.middlewares.throttle import ThrottleMiddleware

    dp.update.outer_middleware(DbSessionMiddleware())
    dp.update.outer_middleware(AuthMiddleware())
    dp.update.outer_middleware(I18nMiddleware())
    dp.message.middleware(ThrottleMiddleware())

    from jobly.bot.handlers import admin, browse, credits, cv, preferences, profile, referral, start, tailor

    dp.include_router(start.router)
    dp.include_router(profile.router)
    dp.include_router(preferences.router)
    dp.include_router(credits.router)
    dp.include_router(cv.router)
    dp.include_router(browse.router)
    dp.include_router(tailor.router)
    dp.include_router(referral.router)
    dp.include_router(admin.router)

    return dp


async def on_startup(bot: Bot) -> None:
    from jobly.db.seed import seed_reference_data

    await seed_reference_data()

    _setup_scheduler(bot)

    logger.info("Bot started successfully")


def _setup_scheduler(bot: Bot) -> None:
    try:
        from apscheduler import AsyncScheduler

        from jobly.workers.scheduler import set_bot

        set_bot(bot)
        scheduler = AsyncScheduler()
        asyncio.get_event_loop().create_task(_start_scheduler(scheduler))
    except ImportError:
        logger.warning("APScheduler not available, skipping scheduled tasks")


async def _start_scheduler(scheduler) -> None:
    from apscheduler.triggers.interval import IntervalTrigger

    from jobly.workers.scheduler import hourly_scrape_job

    async with scheduler:
        await scheduler.add_schedule(
            hourly_scrape_job,
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
