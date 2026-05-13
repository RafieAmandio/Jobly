import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from jobly.bot.middlewares.throttle import ThrottleMiddleware


def _make_message_event(user_id: int):
    from aiogram.types import Message

    event = MagicMock(spec=Message)
    event.from_user = MagicMock()
    event.from_user.id = user_id
    return event


@pytest.mark.asyncio
async def test_throttle_allows_normal_traffic():
    mw = ThrottleMiddleware(rate_limit=5)
    handler = AsyncMock(return_value="ok")
    event = _make_message_event(123)

    result = await mw(handler, event, {})
    assert result == "ok"
    handler.assert_called_once()


@pytest.mark.asyncio
async def test_throttle_blocks_excessive_traffic():
    mw = ThrottleMiddleware(rate_limit=2)
    handler = AsyncMock(return_value="ok")
    event = _make_message_event(456)

    now = time.monotonic()
    mw._user_timestamps[456] = [now, now]

    result = await mw(handler, event, {})
    assert result is None
    handler.assert_not_called()


@pytest.mark.asyncio
async def test_throttle_resets_after_window():
    mw = ThrottleMiddleware(rate_limit=1)
    handler = AsyncMock(return_value="ok")
    event = _make_message_event(789)

    mw._user_timestamps[789] = [time.monotonic() - 120]

    result = await mw(handler, event, {})
    assert result == "ok"
