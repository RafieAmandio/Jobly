from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from jobly.bot.handlers.cv import (
    CVUpdateState,
    cmd_upload_cv,
    on_cv_text_upload,
    on_remove_current_cv,
)
from tests.factories import MemoryFSMContext, make_callback, make_message


@pytest.mark.asyncio
async def test_cmd_upload_cv_sets_text_upload_state(mock_user, mock_session):
    state = MemoryFSMContext()
    msg = make_message(user_id=mock_user.telegram_id)
    mock_session.execute.return_value = Mock(scalar_one_or_none=lambda: None)

    await cmd_upload_cv(msg, state, mock_session, mock_user, "en")

    assert await state.get_state() == "CVUpdateState:waiting"
    msg.answer.assert_called_once()
    assert "cv" in msg.answer.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_on_cv_text_upload_accepts_plain_text(mock_session, mock_user):
    mock_user.onboarding_completed = True
    state = MemoryFSMContext()
    await state.set_state("CVUpdateState:waiting")
    msg = make_message(text="John Doe\nSoftware Engineer\nPython, SQL", user_id=mock_user.telegram_id)

    existing = SimpleNamespace(is_current=True)
    exec_result = Mock()
    exec_result.scalar_one_or_none.return_value = existing
    mock_session.execute.side_effect = [exec_result]
    mock_session.add = Mock()

    await on_cv_text_upload(msg, state, mock_session, mock_user, "en")

    assert existing.is_current is False
    assert mock_session.add.call_count == 1
    assert await state.get_state() is None
    msg.answer.assert_called_once()
    assert "uploaded" in msg.answer.call_args[0][0].lower()


@pytest.mark.asyncio
async def test_cmd_upload_cv_shows_remove_option_when_current_cv_exists(mock_user, mock_session):
    state = MemoryFSMContext()
    msg = make_message(user_id=mock_user.telegram_id)
    mock_session.execute.return_value = Mock(scalar_one_or_none=lambda: SimpleNamespace(is_current=True))

    await cmd_upload_cv(msg, state, mock_session, mock_user, "en")

    assert await state.get_state() == CVUpdateState.waiting.state
    msg.answer.assert_called_once()
    reply_markup = msg.answer.call_args.kwargs["reply_markup"]
    assert reply_markup.inline_keyboard[0][0].callback_data == "cv_remove_current"


@pytest.mark.asyncio
async def test_remove_current_cv_marks_existing_cv_inactive(mock_user, mock_session):
    state = MemoryFSMContext()
    await state.set_state(CVUpdateState.waiting)
    existing = SimpleNamespace(is_current=True)
    mock_session.execute.return_value = Mock(scalar_one_or_none=lambda: existing)
    cb = make_callback(data="cv_remove_current", user_id=mock_user.telegram_id)

    await on_remove_current_cv(cb, state, mock_session, mock_user, "en")

    assert existing.is_current is False
    assert await state.get_state() is None
    cb.message.edit_text.assert_called_once()


@pytest.mark.asyncio
async def test_remove_current_cv_handles_missing_current_cv(mock_user, mock_session):
    state = MemoryFSMContext()
    await state.set_state(CVUpdateState.waiting)
    mock_session.execute.return_value = Mock(scalar_one_or_none=lambda: None)
    cb = make_callback(data="cv_remove_current", user_id=mock_user.telegram_id)

    await on_remove_current_cv(cb, state, mock_session, mock_user, "en")

    assert await state.get_state() == CVUpdateState.waiting.state
    cb.answer.assert_called_once()
    cb.message.edit_text.assert_not_called()
