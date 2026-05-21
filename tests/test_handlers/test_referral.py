import pytest
from sqlalchemy import select

from jobly.bot.handlers.referral import cmd_redeem, cmd_referral
from jobly.models.user import User
from jobly.services.user import create_user
from tests.factories import MockBot, make_message


@pytest.mark.asyncio
async def test_referral_shows_code(seeded_session, test_user):
    msg = make_message(user_id=test_user.telegram_id)
    await cmd_referral(msg, test_user, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert test_user.referral_code in text


@pytest.mark.asyncio
async def test_redeem_success(seeded_session, test_user):
    other_user = await create_user(
        seeded_session,
        telegram_id=777666555,
        full_name="Other User",
        email="other@example.com",
        language="en",
    )
    await seeded_session.flush()

    original_balance = test_user.credit_balance
    other_original = other_user.credit_balance

    bot = MockBot()
    msg = make_message(
        text=f"/redeem {test_user.referral_code}",
        user_id=other_user.telegram_id,
        bot=bot,
    )
    msg.bot = bot

    await cmd_redeem(msg, seeded_session, other_user, "en")

    msg.answer.assert_called()
    assert other_user.credit_balance == other_original + 2
    assert test_user.credit_balance == original_balance + 2
    assert other_user.referred_by == test_user.id


@pytest.mark.asyncio
async def test_redeem_own_code(seeded_session, test_user):
    msg = make_message(
        text=f"/redeem {test_user.referral_code}",
        user_id=test_user.telegram_id,
    )
    await cmd_redeem(msg, seeded_session, test_user, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "own" in text.lower() or "sendiri" in text.lower()


@pytest.mark.asyncio
async def test_redeem_already_used(seeded_session, test_user):
    other = await create_user(
        seeded_session, telegram_id=111222333, full_name="Referrer", language="en"
    )
    await seeded_session.flush()
    test_user.referred_by = other.id
    await seeded_session.flush()

    msg = make_message(text="/redeem SOMECODE", user_id=test_user.telegram_id)
    await cmd_redeem(msg, seeded_session, test_user, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "already" in text.lower() or "sudah" in text.lower()


@pytest.mark.asyncio
async def test_redeem_invalid_code(seeded_session, test_user):
    msg = make_message(text="/redeem INVALIDCODE", user_id=test_user.telegram_id)
    await cmd_redeem(msg, seeded_session, test_user, "en")

    msg.answer.assert_called_once()
    text = msg.answer.call_args[0][0]
    assert "invalid" in text.lower() or "tidak valid" in text.lower()
