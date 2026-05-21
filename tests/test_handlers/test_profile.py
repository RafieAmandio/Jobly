import pytest

from jobly.bot.handlers.profile import cmd_help, cmd_profile
from jobly.bot.handlers.credits import cmd_credits
from tests.factories import MockBot, make_message


@pytest.mark.asyncio
async def test_cmd_profile(seeded_session, test_user):
    msg = make_message(user_id=test_user.telegram_id)
    await cmd_profile(msg, seeded_session, test_user, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "Test User" in text
    assert "test@example.com" in text


@pytest.mark.asyncio
async def test_cmd_credits(seeded_session, test_user):
    msg = make_message(user_id=test_user.telegram_id)
    await cmd_credits(msg, test_user, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "3" in text


@pytest.mark.asyncio
async def test_cmd_help():
    msg = make_message()
    await cmd_help(msg, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "/start" in text
    assert "/profile" in text
    assert "/credits" in text


@pytest.mark.asyncio
async def test_not_registered_profile(seeded_session):
    msg = make_message()
    await cmd_profile(msg, seeded_session, None, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "not registered" in text.lower() or "belum terdaftar" in text.lower()


@pytest.mark.asyncio
async def test_not_registered_credits():
    msg = make_message()
    await cmd_credits(msg, None, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "not registered" in text.lower() or "belum terdaftar" in text.lower()
