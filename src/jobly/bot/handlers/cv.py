from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.i18n.strings import t
from jobly.models.cv import CV
from jobly.models.user import User

router = Router()


class CVUpdateState(StatesGroup):
    waiting = State()


def cv_actions_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    remove_text = "🗑 Remove current CV" if lang == "en" else "🗑 Hapus CV saat ini"
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=remove_text, callback_data="cv_remove_current")]
        ]
    )


async def _get_current_cv(session: AsyncSession, db_user: User) -> CV | None:
    return (
        await session.execute(select(CV).where(CV.user_id == db_user.id, CV.is_current))
    ).scalar_one_or_none()


@router.message(Command("upload_cv"))
async def cmd_upload_cv(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User | None,
    lang: str,
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    await state.set_state(CVUpdateState.waiting)
    current_cv = await _get_current_cv(session, db_user)
    reply_markup = cv_actions_keyboard(lang) if current_cv else None
    await message.answer(t("ask_cv", lang), reply_markup=reply_markup)


@router.callback_query(F.data == "cv_remove_current")
async def on_remove_current_cv(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    db_user: User | None,
    lang: str,
) -> None:
    if not db_user:
        await callback.answer()
        return

    current_cv = await _get_current_cv(session, db_user)
    if not current_cv:
        await callback.answer()
        return

    current_cv.is_current = False
    await state.clear()
    await callback.message.edit_text(t("cv_removed", lang))
    await callback.answer()


@router.message(F.document, ~F.state)
@router.message(CVUpdateState.waiting, F.document)
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
    if doc.mime_type != "application/pdf":
        await message.answer("Please upload a PDF file." if lang == "en" else "Mohon upload file PDF.")
        return

    file = await message.bot.download(doc)
    pdf_bytes = file.read()

    from jobly.services.cv_parser import extract_text_from_pdf

    cv_text = extract_text_from_pdf(pdf_bytes)

    existing = await _get_current_cv(session, db_user)
    if existing:
        existing.is_current = False

    cv = CV(user_id=db_user.id, raw_text=cv_text, is_current=True)
    session.add(cv)
    await state.clear()
    await message.answer(t("cv_uploaded", lang))


@router.message(Command("view_cv"))
async def cmd_view_cv(message: Message, session: AsyncSession, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    cv = await _get_current_cv(session, db_user)

    if not cv:
        await message.answer(t("no_cv_uploaded", lang))
        return

    preview = cv.raw_text[:2000]
    if len(cv.raw_text) > 2000:
        preview += "\n\n... (truncated)"
    await message.answer(f"📄 CV Preview:\n\n{preview}")
