from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from jobly.bot.handlers.tailor import on_cover_letter, on_tailor_cv
from jobly.models.credit import CreditTransaction
from jobly.models.notification import TailoringHistory
from tests.factories import MockBot, make_callback


@pytest.mark.asyncio
@patch("jobly.services.cv_tailor.tailor_cv_content")
@patch("jobly.services.doc_generator.generate_cv_pdf")
@patch("jobly.services.doc_generator.generate_cv_docx")
async def test_tailor_cv_success(mock_docx, mock_pdf, mock_ai, seeded_session, test_user, test_job, test_cv):
    mock_ai.return_value = {"summary": "Tailored summary", "experience": [], "skills": [], "education": []}
    mock_docx.return_value = b"fake-docx"
    mock_pdf.return_value = b"fake-pdf"
    bot = MockBot()
    cb = make_callback(
        data=f"tailor:{test_job.id}", user_id=test_user.telegram_id, bot=bot
    )

    await on_tailor_cv(cb, seeded_session, test_user, "en")

    mock_ai.assert_called_once()
    assert test_user.credit_balance == 2
    cb.message.answer_document.assert_called()


@pytest.mark.asyncio
async def test_tailor_insufficient_credits(seeded_session, test_user, test_job, test_cv):
    test_user.credit_balance = 0
    await seeded_session.flush()

    bot = MockBot()
    cb = make_callback(
        data=f"tailor:{test_job.id}", user_id=test_user.telegram_id, bot=bot
    )

    await on_tailor_cv(cb, seeded_session, test_user, "en")

    cb.message.answer.assert_called()
    call_text = cb.message.answer.call_args[0][0]
    assert "insufficient" in call_text.lower() or "tidak cukup" in call_text.lower()
    assert test_user.credit_balance == 0


@pytest.mark.asyncio
@patch("jobly.services.cover_letter.generate_cover_letter_content")
@patch("jobly.services.doc_generator.generate_cover_letter_pdf")
@patch("jobly.services.doc_generator.generate_cover_letter_docx")
async def test_cover_letter_success(mock_docx, mock_pdf, mock_ai, seeded_session, test_user, test_job, test_cv):
    mock_ai.return_value = "Dear Hiring Manager, I am writing to express my interest."
    mock_docx.return_value = b"fake-cl-docx"
    mock_pdf.return_value = b"fake-cl-pdf"
    bot = MockBot()
    cb = make_callback(
        data=f"cover:{test_job.id}", user_id=test_user.telegram_id, bot=bot
    )

    await on_cover_letter(cb, seeded_session, test_user, "en")

    mock_ai.assert_called_once()
    assert test_user.credit_balance == 2
    cb.message.answer_document.assert_called()


@pytest.mark.asyncio
async def test_tailor_no_cv(seeded_session, test_user, test_job):
    bot = MockBot()
    cb = make_callback(
        data=f"tailor:{test_job.id}", user_id=test_user.telegram_id, bot=bot
    )

    await on_tailor_cv(cb, seeded_session, test_user, "en")

    cb.message.answer.assert_called()
    call_text = cb.message.answer.call_args[0][0]
    assert "upload" in call_text.lower() or "no cv" in call_text.lower() or "belum upload" in call_text.lower()
