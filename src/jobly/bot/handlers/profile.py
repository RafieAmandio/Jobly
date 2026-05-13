from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.bot.keyboards.onboarding import language_keyboard
from jobly.constants.categories import CATEGORIES
from jobly.constants.levels import EXPERIENCE_LEVELS
from jobly.i18n.strings import t
from jobly.models.reference import Category, Location, WorkArrangement
from jobly.models.user import User, UserCategory, UserLocation, UserWorkArrangement

router = Router()


@router.message(Command("profile"))
async def cmd_profile(message: Message, session: AsyncSession, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    cat_ids_result = await session.execute(
        select(UserCategory.category_id).where(UserCategory.user_id == db_user.id)
    )
    cat_ids = [row[0] for row in cat_ids_result.all()]
    cat_names = []
    if cat_ids:
        cats_result = await session.execute(select(Category).where(Category.id.in_(cat_ids)))
        cat_names = [
            c.name_id if lang == "id" else c.name_en for c in cats_result.scalars().all()
        ]

    loc_ids_result = await session.execute(
        select(UserLocation.location_id).where(UserLocation.user_id == db_user.id)
    )
    loc_ids = [row[0] for row in loc_ids_result.all()]
    loc_names = []
    if loc_ids:
        locs_result = await session.execute(select(Location).where(Location.id.in_(loc_ids)))
        loc_names = [l.city for l in locs_result.scalars().all()]

    arr_ids_result = await session.execute(
        select(UserWorkArrangement.arrangement_id).where(
            UserWorkArrangement.user_id == db_user.id
        )
    )
    arr_ids = [row[0] for row in arr_ids_result.all()]
    arr_names = []
    if arr_ids:
        arrs_result = await session.execute(
            select(WorkArrangement).where(WorkArrangement.id.in_(arr_ids))
        )
        arr_names = [
            a.label_id if lang == "id" else a.label_en for a in arrs_result.scalars().all()
        ]

    exp_label = db_user.preferences.experience_level if db_user.preferences else "-"
    for lvl in EXPERIENCE_LEVELS:
        if db_user.preferences and lvl["slug"] == db_user.preferences.experience_level:
            exp_label = lvl["label_id" if lang == "id" else "label_en"]
            break

    await message.answer(
        t(
            "profile_summary",
            lang,
            name=db_user.full_name,
            email=db_user.email or "-",
            level=exp_label,
            categories=", ".join(cat_names) if cat_names else "-",
            locations=", ".join(loc_names) if loc_names else "-",
            arrangements=", ".join(arr_names) if arr_names else "-",
            credits=str(db_user.credit_balance),
        )
    )


@router.message(Command("language"))
async def cmd_language(message: Message, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return
    await message.answer(
        t("ask_language", lang),
        reply_markup=language_keyboard(),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("lang:"))
async def on_language_change(
    callback: CallbackQuery, session: AsyncSession, db_user: User | None
) -> None:
    if not db_user:
        await callback.answer()
        return
    new_lang = callback.data.split(":")[1]
    from jobly.services.user import update_language

    await update_language(session, db_user, new_lang)
    await callback.message.edit_text(t("language_changed", new_lang))
    await callback.answer()


@router.message(Command("help"))
async def cmd_help(message: Message, lang: str) -> None:
    await message.answer(t("help", lang))


@router.message(Command("delete_account"))
async def cmd_delete(message: Message, session: AsyncSession, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Yes, delete" if lang == "en" else "Ya, hapus", callback_data="delete_yes"),
            InlineKeyboardButton(text="Cancel" if lang == "en" else "Batal", callback_data="delete_no"),
        ]
    ])
    await message.answer(t("confirm_delete", lang), reply_markup=kb)


@router.callback_query(lambda c: c.data == "delete_yes")
async def on_delete_confirm(
    callback: CallbackQuery, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await callback.answer()
        return
    from jobly.services.user import delete_user

    await delete_user(session, db_user)
    await callback.message.edit_text(t("account_deleted", lang))
    await callback.answer()


@router.callback_query(lambda c: c.data == "delete_no")
async def on_delete_cancel(callback: CallbackQuery, lang: str) -> None:
    await callback.message.delete()
    await callback.answer()
