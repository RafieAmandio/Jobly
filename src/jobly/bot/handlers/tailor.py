import logging
import uuid

from aiogram import F, Router
from aiogram.types import BufferedInputFile, CallbackQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.i18n.strings import t
from jobly.models.cv import CV
from jobly.models.job import Job
from jobly.models.user import User
from jobly.services.credit import add_credit, deduct_credit

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.startswith("tailor:"))
async def on_tailor_cv(
    callback: CallbackQuery, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await callback.answer()
        return

    job_id = callback.data.split(":")[1]
    job = await session.get(Job, uuid.UUID(job_id))
    if not job:
        await callback.answer("Job not found")
        return

    cv = (
        await session.execute(
            select(CV).where(CV.user_id == db_user.id, CV.is_current == True)
        )
    ).scalar_one_or_none()
    if not cv:
        await callback.message.answer(t("no_cv_uploaded", lang))
        await callback.answer()
        return

    if not await deduct_credit(
        session, db_user, 1, "tailor_cv", str(job.id), f"CV tailor: {job.title}"
    ):
        await callback.message.answer(t("insufficient_credits", lang, needed=1))
        await callback.answer()
        return

    await callback.message.answer(t("tailoring_started", lang))
    await callback.answer()

    from jobly.services.cv_tailor import tailor_cv

    try:
        result = await tailor_cv(
            session=session,
            user=db_user,
            cv=cv,
            job=job,
            lang=lang,
        )
    except Exception:
        # e.g. the AI provider returning 429; fall through to the refund below
        logger.exception("tailor_cv failed for job %s", job.id)
        result = None

    if result:
        if result.get("docx"):
            await callback.message.answer_document(
                BufferedInputFile(result["docx"], filename=f"CV_Tailored_{job.company}.docx")
            )
        if result.get("pdf"):
            await callback.message.answer_document(
                BufferedInputFile(result["pdf"], filename=f"CV_Tailored_{job.company}.pdf")
            )
        await callback.message.answer(t("tailoring_complete", lang))
    else:
        # The credit was taken up front; a failed generation must not cost the user.
        await add_credit(session, db_user, 1, "refund", str(job.id), f"Refund, CV tailor failed: {job.title}")
        error = (
            "Gagal membuat CV. Kredit kamu sudah dikembalikan."
            if lang == "id"
            else "Failed to generate CV. Your credit has been refunded."
        )
        await callback.message.answer(error)


@router.callback_query(F.data.startswith("cover:"))
async def on_cover_letter(
    callback: CallbackQuery, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await callback.answer()
        return

    job_id = callback.data.split(":")[1]
    job = await session.get(Job, uuid.UUID(job_id))
    if not job:
        await callback.answer("Job not found")
        return

    cv = (
        await session.execute(
            select(CV).where(CV.user_id == db_user.id, CV.is_current == True)
        )
    ).scalar_one_or_none()
    if not cv:
        await callback.message.answer(t("no_cv_uploaded", lang))
        await callback.answer()
        return

    if not await deduct_credit(
        session, db_user, 1, "cover_letter", str(job.id), f"Cover letter: {job.title}"
    ):
        await callback.message.answer(t("insufficient_credits", lang, needed=1))
        await callback.answer()
        return

    await callback.message.answer(t("cover_letter_started", lang))
    await callback.answer()

    from jobly.services.cover_letter import generate_cover_letter

    try:
        result = await generate_cover_letter(
            session=session,
            user=db_user,
            cv=cv,
            job=job,
            lang=lang,
        )
    except Exception:
        # e.g. the AI provider returning 429; fall through to the refund below
        logger.exception("generate_cover_letter failed for job %s", job.id)
        result = None

    if result:
        if result.get("docx"):
            await callback.message.answer_document(
                BufferedInputFile(result["docx"], filename=f"Cover_Letter_{job.company}.docx")
            )
        if result.get("pdf"):
            await callback.message.answer_document(
                BufferedInputFile(result["pdf"], filename=f"Cover_Letter_{job.company}.pdf")
            )
        await callback.message.answer(t("cover_letter_complete", lang))
    else:
        await add_credit(
            session, db_user, 1, "refund", str(job.id), f"Refund, cover letter failed: {job.title}"
        )
        error = (
            "Gagal membuat cover letter. Kredit kamu sudah dikembalikan."
            if lang == "id"
            else "Failed to generate cover letter. Your credit has been refunded."
        )
        await callback.message.answer(error)
