from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

import pytest

from jobly.bot.handlers.admin import _resolve_user, cmd_give_credits
from tests.factories import make_message


def _result(user):
    scalars = Mock()
    scalars.first.return_value = user
    result = Mock()
    result.scalars.return_value = scalars
    result.scalar_one_or_none.return_value = user
    return result


@pytest.mark.asyncio
async def test_resolve_user_accepts_numeric_id(mock_session):
    target = SimpleNamespace(telegram_id=123, full_name="Someone")
    mock_session.execute.return_value = _result(target)

    assert await _resolve_user(mock_session, "123") is target


@pytest.mark.asyncio
@pytest.mark.parametrize("token", ["@SomeOne", "someone", "@someone"])
async def test_resolve_user_accepts_username_any_case(mock_session, token):
    """Admins type the @handle they can see; the numeric id is not visible in Telegram."""
    target = SimpleNamespace(telegram_id=123, telegram_username="someone")
    mock_session.execute.return_value = _result(target)

    assert await _resolve_user(mock_session, token) is target


@pytest.mark.asyncio
async def test_give_credits_by_username_adds_credits(mock_session, mock_user):
    mock_user.credit_balance = 5
    mock_user.full_name = "Dharma"
    mock_session.execute.return_value = _result(mock_user)
    mock_session.add = Mock()
    msg = make_message(text="/give_credits @dharma 50")
    msg.answer = AsyncMock()

    await cmd_give_credits(msg, mock_session)

    assert mock_user.credit_balance == 55
    reply = msg.answer.await_args[0][0]
    assert "50" in reply and "55" in reply


@pytest.mark.asyncio
async def test_give_credits_rejects_bad_amount(mock_session):
    msg = make_message(text="/give_credits @dharma notanumber")
    msg.answer = AsyncMock()

    await cmd_give_credits(msg, mock_session)

    assert "Invalid amount" in msg.answer.await_args[0][0]


@pytest.mark.asyncio
async def test_give_credits_reports_unknown_user(mock_session):
    mock_session.execute.return_value = _result(None)
    msg = make_message(text="/give_credits @nobody 10")
    msg.answer = AsyncMock()

    await cmd_give_credits(msg, mock_session)

    assert "not found" in msg.answer.await_args[0][0]
