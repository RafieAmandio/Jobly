from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.i18n.strings import t
from jobly.models.cv import CV
from jobly.models.user import User

router = Router()


@router.message(Command("upload_cv"))
async def cmd_upload_cv(message: Message, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return
    await message.answer(t("ask_cv", lang))


@router.message(F.document, ~F.state)
async def on_cv_upload(message: Message, session: AsyncSession, db_user: User | None, lang: str) -> None:
    if not db_user or not db_user.onboarding_completed:
        return

    doc = message.document
    if doc.mime_type != "application/pdf":
        await message.answer("Please upload a PDF file." if lang == "en" else "Mohon upload file PDF.")
        return

    file = await message.bot.download(doc)
    pdf_bytes = file.read()

    from jobly.services.cv_parser import extract_text_from_pdf

    cv_text = extract_text_from_pdf(pdf_bytes)

    await session.execute(
        select(CV).where(CV.user_id == db_user.id, CV.is_current == True)
    )
    existing = (
        await session.execute(
            select(CV).where(CV.user_id == db_user.id, CV.is_current == True)
        )
    ).scalar_one_or_none()
    if existing:
        existing.is_current = False

    cv = CV(user_id=db_user.id, raw_text=cv_text, is_current=True)
    session.add(cv)

    await message.answer(t("cv_uploaded", lang))


@router.message(Command("view_cv"))
async def cmd_view_cv(message: Message, session: AsyncSession, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    cv = (
        await session.execute(
            select(CV).where(CV.user_id == db_user.id, CV.is_current == True)
        )
    ).scalar_one_or_none()

    if not cv:
        await message.answer(t("no_cv_uploaded", lang))
        return

    preview = cv.raw_text[:2000]
    if len(cv.raw_text) > 2000:
        preview += "\n\n... (truncated)"
    await message.answer(f"📄 CV Preview:\n\n{preview}")
