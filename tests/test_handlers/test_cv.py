from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from jobly.bot.handlers.cv import CVUpdateState, cmd_upload_cv, on_cv_text_upload
from tests.factories import MemoryFSMContext, make_message


@pytest.mark.asyncio
async def test_cmd_upload_cv_sets_waiting_state(mock_user):
    state = MemoryFSMContext()
    msg = make_message(user_id=mock_user.telegram_id)

    await cmd_upload_cv(msg, state, mock_user, "en")

    assert await state.get_state() == CVUpdateState.waiting.state
    msg.answer.assert_called_once()


@pytest.mark.asyncio
@patch("jobly.bot.handlers.cv.prepare_cv_text", new_callable=AsyncMock)
async def test_on_cv_text_upload_enriches_linkedin_input(mock_prepare_cv_text, mock_session, mock_user):
    mock_prepare_cv_text.return_value = "LinkedIn profile source\nProfile title: John Doe"
    state = MemoryFSMContext()
    await state.set_state(CVUpdateState.waiting)
    msg = make_message(text="https://www.linkedin.com/in/johndoe", user_id=mock_user.telegram_id)

    existing = SimpleNamespace(is_current=True)
    exec_result = Mock()
    exec_result.scalar_one_or_none.return_value = existing
    mock_session.execute.side_effect = [None, exec_result]
    mock_session.add = Mock()

    await on_cv_text_upload(msg, state, mock_session, mock_user, "en")

    mock_prepare_cv_text.assert_awaited_once_with("https://www.linkedin.com/in/johndoe")
    assert existing.is_current is False
    assert mock_session.add.call_count == 1
    assert await state.get_state() is None
    msg.answer.assert_called_once()
