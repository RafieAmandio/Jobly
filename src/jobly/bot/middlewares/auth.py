from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.services.user import get_user_by_telegram_id

SKIP_AUTH_COMMANDS = {"/start", "/help"}


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        session: AsyncSession = data.get("session")
        if not session:
            return await handler(event, data)

        if isinstance(event, Message) and event.text in SKIP_AUTH_COMMANDS:
            return await handler(event, data)

        telegram_user = data.get("event_from_user")
        if telegram_user:
            user = await get_user_by_telegram_id(session, telegram_user.id)
            data["db_user"] = user

        return await handler(event, data)
