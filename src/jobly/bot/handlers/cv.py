from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.i18n.strings import t
from jobly.models.cv import CV
from jobly.models.user import User
from jobly.services.cv_input import prepare_cv_text
from jobly.services.cv_parser import SUPPORTED_CV_MIME_TYPES, extract_text_from_upload

router = Router()


class CVUpdateState(StatesGroup):
    waiting = State()


async def _store_current_cv(session: AsyncSession, db_user: User, cv_text: str) -> None:
    existing = (
        await session.execute(select(CV).where(CV.user_id == db_user.id, CV.is_current))
    ).scalar_one_or_none()
    if existing:
        existing.is_current = False

    cv = CV(user_id=db_user.id, raw_text=cv_text, is_current=True)
    session.add(cv)


@router.message(Command("upload_cv"))
async def cmd_upload_cv(
    message: Message, state: FSMContext, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return
    await state.set_state(CVUpdateState.waiting)
    await message.answer(t("ask_cv", lang))


@router.message(CVUpdateState.waiting, F.document)
@router.message(F.document, ~F.state)
async def on_cv_upload(
    message: Message,
    session: AsyncSession,
    db_user: User | None,
    lang: str,
    state: FSMContext,
) -> None:
    if not db_user or not db_user.onboarding_completed:
        return

    doc = message.document
    if doc.mime_type not in SUPPORTED_CV_MIME_TYPES:
        await message.answer(t("invalid_cv_upload", lang))
        return

    file = await message.bot.download(doc)
    file_bytes = file.read()
    cv_text = extract_text_from_upload(file_bytes, doc.mime_type)
    await _store_current_cv(session, db_user, cv_text)
    await state.clear()
    await message.answer(t("cv_uploaded", lang))


@router.message(CVUpdateState.waiting, F.photo)
async def on_cv_photo_upload(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User | None,
    lang: str,
) -> None:
    del session, db_user
    await message.answer(t("invalid_cv_upload", lang))
    await state.set_state(CVUpdateState.waiting)


@router.message(CVUpdateState.waiting, F.text)
async def on_cv_text_upload(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User | None,
    lang: str,
) -> None:
    if not db_user or not db_user.onboarding_completed:
        return

    cv_text = await prepare_cv_text(message.text.strip() if message.text else "")
    await _store_current_cv(session, db_user, cv_text)
    await state.clear()
    await message.answer(t("cv_uploaded", lang))


@router.message(Command("view_cv"))
async def cmd_view_cv(
    message: Message, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    cv = (
        await session.execute(select(CV).where(CV.user_id == db_user.id, CV.is_current))
    ).scalar_one_or_none()

    if not cv:
        await message.answer(t("no_cv_uploaded", lang))
        return

    preview = cv.raw_text[:2000]
    if len(cv.raw_text) > 2000:
        preview += "\n\n... (truncated)"
    await message.answer(f"📄 CV Preview:\n\n{preview}")
