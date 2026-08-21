from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from jobly.bot.handlers.cv import CVUpdateState, cmd_upload_cv, on_cv_photo_upload
from tests.factories import MemoryFSMContext, make_message


@pytest.mark.asyncio
async def test_cmd_upload_cv_sets_waiting_state(mock_user):
    state = MemoryFSMContext()
    msg = make_message(user_id=mock_user.telegram_id)

    await cmd_upload_cv(msg, state, mock_user, "en")

    assert await state.get_state() == CVUpdateState.waiting.state
    msg.answer.assert_called_once()


@pytest.mark.asyncio
async def test_on_cv_photo_upload_rejects_photo_and_keeps_waiting_state(
    mock_session, mock_user
):
    state = MemoryFSMContext()
    await state.set_state(CVUpdateState.waiting)
    msg = make_message(user_id=mock_user.telegram_id)
    msg.photo = [SimpleNamespace(file_id="photo-1")]
    mock_session.add = Mock()

    await on_cv_photo_upload(msg, state, mock_session, mock_user, "en")

    assert await state.get_state() == CVUpdateState.waiting.state
    mock_session.add.assert_not_called()
    msg.answer.assert_called_once_with("Please upload a PDF or DOCX file.")
