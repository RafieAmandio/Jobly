from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from jobly.bot.handlers.cv import cmd_upload_cv, on_cv_text_upload
from tests.factories import MemoryFSMContext, make_message


@pytest.mark.asyncio
async def test_cmd_upload_cv_sets_text_upload_state(mock_user):
    state = MemoryFSMContext()
    msg = make_message(user_id=mock_user.telegram_id)

    await cmd_upload_cv(msg, state, mock_user, "en")

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
    mock_session.execute.side_effect = [None, exec_result]
    mock_session.add = Mock()

    await on_cv_text_upload(msg, state, mock_session, mock_user, "en")

    assert existing.is_current is False
    assert mock_session.add.call_count == 1
    assert await state.get_state() is None
    msg.answer.assert_called_once()
    assert "uploaded" in msg.answer.call_args[0][0].lower()
