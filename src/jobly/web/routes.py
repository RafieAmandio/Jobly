import hashlib
import hmac
import json
import logging

from aiohttp import web

from jobly.config import settings
from jobly.db.session import async_session
from jobly.services.payment import handle_xendit_webhook

logger = logging.getLogger(__name__)


async def xendit_webhook(request: web.Request) -> web.Response:
    callback_token = request.headers.get("x-callback-token", "")
    if callback_token != settings.xendit.webhook_token:
        logger.warning("Invalid Xendit callback token")
        return web.Response(status=403, text="Invalid token")

    try:
        payload = await request.json()
    except json.JSONDecodeError:
        return web.Response(status=400, text="Invalid JSON")

    async with async_session() as session:
        success = await handle_xendit_webhook(session, payload)
        await session.commit()

    if success:
        return web.Response(status=200, text="OK")
    return web.Response(status=404, text="Payment not found")


async def health_check(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


def setup_routes(app: web.Application) -> None:
    app.router.add_post("/webhooks/xendit", xendit_webhook)
    app.router.add_get("/health", health_check)
