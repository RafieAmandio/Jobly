import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

MAX_REQUESTS_PER_MINUTE = 20


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: int = MAX_REQUESTS_PER_MINUTE) -> None:
        self._rate_limit = rate_limit
        self._user_timestamps: dict[int, list[float]] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not isinstance(event, Message):
            return await handler(event, data)

        user_id = event.from_user.id if event.from_user else None
        if not user_id:
            return await handler(event, data)

        now = time.monotonic()
        timestamps = self._user_timestamps.get(user_id, [])
        cutoff = now - 60
        timestamps = [ts for ts in timestamps if ts > cutoff]

        if len(timestamps) >= self._rate_limit:
            return None

        timestamps.append(now)
        self._user_timestamps[user_id] = timestamps

        return await handler(event, data)
