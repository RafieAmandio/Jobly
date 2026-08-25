from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from jobly.bot.handlers.cv import (
    CVUpdateState,
    cmd_upload_cv,
    on_remove_current_cv,
)
from tests.factories import MemoryFSMContext, make_callback, make_message


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
