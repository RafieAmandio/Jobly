from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

import pytest

from jobly.bot.handlers.cv import on_cv_upload
from jobly.bot.handlers.start import OnboardingState, on_cv_pdf
from tests.factories import MemoryFSMContext, make_message


@pytest.mark.asyncio
@patch("jobly.bot.handlers.cv.extract_text_from_docx")
async def test_on_cv_upload_accepts_docx(mock_extract, mock_session, mock_user):
    mock_extract.return_value = "John Doe CV"
    mock_user.onboarding_completed = True

    bot = AsyncMock()
    bot.download.return_value = SimpleNamespace(read=lambda: b"fake-docx")
    msg = make_message(bot=bot)
    msg.document = SimpleNamespace(
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    existing = SimpleNamespace(is_current=True)
    exec_result = Mock()
    exec_result.scalar_one_or_none.return_value = existing
    mock_session.execute.side_effect = [None, exec_result]
    mock_session.add = Mock()

    await on_cv_upload(msg, mock_session, mock_user, "en")

    mock_extract.assert_called_once_with(b"fake-docx")
    assert existing.is_current is False
    assert mock_session.add.call_count == 1
    msg.answer.assert_called_once()
    assert "uploaded" in msg.answer.call_args[0][0].lower()


@pytest.mark.asyncio
@patch("jobly.bot.handlers.start.extract_text_from_docx")
async def test_onboarding_cv_upload_accepts_docx(mock_extract):
    mock_extract.return_value = "Updated CV text"

    state = MemoryFSMContext()
    await state.set_state(OnboardingState.cv_upload)
    await state.set_data({
        "language": "en",
        "selected_categories": [],
        "selected_locations": [],
        "experience_level": "mid",
    })

    bot = AsyncMock()
    bot.download.return_value = SimpleNamespace(read=lambda: b"fake-docx")
    msg = make_message(bot=bot)
    msg.document = SimpleNamespace(
        mime_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

    with patch("jobly.bot.handlers.start._show_confirmation", new=AsyncMock()) as mock_show_confirmation:
        await on_cv_pdf(msg, state, AsyncMock())

    mock_extract.assert_called_once_with(b"fake-docx")
    data = await state.get_data()
    assert data["cv_text"] == "Updated CV text"
    mock_show_confirmation.assert_awaited_once()
