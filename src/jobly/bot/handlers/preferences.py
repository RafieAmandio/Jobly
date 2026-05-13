from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.bot.keyboards.onboarding import (
    category_keyboard,
    experience_keyboard,
    location_keyboard,
    salary_keyboard,
    work_arrangement_keyboard,
)
from jobly.constants.categories import CATEGORIES
from jobly.constants.levels import EXPERIENCE_LEVELS
from jobly.constants.locations import LOCATIONS
from jobly.i18n.strings import t
from jobly.models.reference import Category, Location, WorkArrangement
from jobly.models.user import User, UserCategory, UserLocation, UserPreference, UserWorkArrangement

router = Router()


class EditPrefState(StatesGroup):
    choosing = State()
    categories = State()
    experience = State()
    locations = State()
    arrangements = State()
    salary = State()


PREF_OPTIONS = {
    "id": [
        ("edit_cat", "📂 Kategori Pekerjaan"),
        ("edit_exp", "📊 Level Pengalaman"),
        ("edit_loc", "📍 Lokasi"),
        ("edit_arr", "💼 Jenis Kerja"),
        ("edit_sal", "💰 Rentang Gaji"),
    ],
    "en": [
        ("edit_cat", "📂 Job Categories"),
        ("edit_exp", "📊 Experience Level"),
        ("edit_loc", "📍 Locations"),
        ("edit_arr", "💼 Work Arrangements"),
        ("edit_sal", "💰 Salary Range"),
    ],
}


def edit_menu_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    options = PREF_OPTIONS.get(lang, PREF_OPTIONS["id"])
    rows = [[InlineKeyboardButton(text=label, callback_data=cb)] for cb, label in options]
    done_text = "✅ Selesai" if lang == "id" else "✅ Done"
    rows.append([InlineKeyboardButton(text=done_text, callback_data="edit_done")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@router.message(Command("edit_preferences"))
async def cmd_edit_preferences(
    message: Message, state: FSMContext, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return
    await state.set_state(EditPrefState.choosing)
    prompt = "Apa yang ingin kamu ubah?" if lang == "id" else "What would you like to change?"
    await message.answer(prompt, reply_markup=edit_menu_keyboard(lang))


@router.callback_query(EditPrefState.choosing, F.data == "edit_cat")
async def on_edit_categories(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(selected_categories=set())
    await state.set_state(EditPrefState.categories)
    await callback.message.edit_text(
        t("ask_categories", lang),
        reply_markup=category_keyboard(page=0, lang=lang),
    )
    await callback.answer()


@router.callback_query(EditPrefState.categories, F.data.startswith("cat:"))
async def on_edit_cat_select(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    idx = int(callback.data.split(":")[1])
    selected: set[int] = data.get("selected_categories", set())
    selected.symmetric_difference_update({idx})
    await state.update_data(selected_categories=selected)
    page = data.get("cat_page", 0)
    await callback.message.edit_reply_markup(
        reply_markup=category_keyboard(page=page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.categories, F.data.startswith("cat_page:"))
async def on_edit_cat_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    page = int(callback.data.split(":")[1])
    selected: set[int] = data.get("selected_categories", set())
    await state.update_data(cat_page=page)
    await callback.message.edit_reply_markup(
        reply_markup=category_keyboard(page=page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.categories, F.data == "cat_done")
async def on_edit_cat_done(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User, lang: str
) -> None:
    data = await state.get_data()
    selected_indices: set[int] = data.get("selected_categories", set())

    await session.execute(delete(UserCategory).where(UserCategory.user_id == db_user.id))
    cats = {c.slug: c.id for c in (await session.execute(select(Category))).scalars().all()}
    for idx in selected_indices:
        slug = CATEGORIES[idx]["slug"]
        if slug in cats:
            session.add(UserCategory(user_id=db_user.id, category_id=cats[slug]))

    await state.set_state(EditPrefState.choosing)
    updated = "Kategori diperbarui! ✅" if lang == "id" else "Categories updated! ✅"
    await callback.message.edit_text(
        f"{updated}\n\n{'Apa lagi?' if lang == 'id' else 'Anything else?'}",
        reply_markup=edit_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(EditPrefState.choosing, F.data == "edit_exp")
async def on_edit_experience(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(EditPrefState.experience)
    await callback.message.edit_text(
        t("ask_experience", lang), reply_markup=experience_keyboard(lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.experience, F.data.startswith("exp:"))
async def on_edit_exp_select(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User, lang: str
) -> None:
    slug = callback.data.split(":")[1]
    if db_user.preferences:
        db_user.preferences.experience_level = slug
    else:
        session.add(UserPreference(user_id=db_user.id, experience_level=slug))

    await state.set_state(EditPrefState.choosing)
    updated = "Level diperbarui! ✅" if lang == "id" else "Experience updated! ✅"
    await callback.message.edit_text(
        f"{updated}\n\n{'Apa lagi?' if lang == 'id' else 'Anything else?'}",
        reply_markup=edit_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(EditPrefState.choosing, F.data == "edit_loc")
async def on_edit_locations(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(selected_locations=set())
    await state.set_state(EditPrefState.locations)
    await callback.message.edit_text(
        t("ask_locations", lang), reply_markup=location_keyboard(page=0, lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.locations, F.data.startswith("loc:"))
async def on_edit_loc_select(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    idx = int(callback.data.split(":")[1])
    selected: set[int] = data.get("selected_locations", set())
    selected.symmetric_difference_update({idx})
    await state.update_data(selected_locations=selected)
    page = data.get("loc_page", 0)
    await callback.message.edit_reply_markup(
        reply_markup=location_keyboard(page=page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.locations, F.data.startswith("loc_page:"))
async def on_edit_loc_page(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    page = int(callback.data.split(":")[1])
    selected: set[int] = data.get("selected_locations", set())
    await state.update_data(loc_page=page)
    await callback.message.edit_reply_markup(
        reply_markup=location_keyboard(page=page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.locations, F.data == "loc_done")
async def on_edit_loc_done(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User, lang: str
) -> None:
    data = await state.get_data()
    selected_indices: set[int] = data.get("selected_locations", set())

    await session.execute(delete(UserLocation).where(UserLocation.user_id == db_user.id))
    locs = {l.city: l.id for l in (await session.execute(select(Location))).scalars().all()}
    for idx in selected_indices:
        city = LOCATIONS[idx]["city"]
        if city in locs:
            session.add(UserLocation(user_id=db_user.id, location_id=locs[city]))

    await state.set_state(EditPrefState.choosing)
    updated = "Lokasi diperbarui! ✅" if lang == "id" else "Locations updated! ✅"
    await callback.message.edit_text(
        f"{updated}\n\n{'Apa lagi?' if lang == 'id' else 'Anything else?'}",
        reply_markup=edit_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(EditPrefState.choosing, F.data == "edit_arr")
async def on_edit_arrangements(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(selected_arrangements=set())
    await state.set_state(EditPrefState.arrangements)
    await callback.message.edit_text(
        t("ask_work_arrangement", lang), reply_markup=work_arrangement_keyboard(lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.arrangements, F.data.startswith("arr:"))
async def on_edit_arr_select(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    name = callback.data.split(":")[1]
    selected: set[str] = data.get("selected_arrangements", set())
    selected.symmetric_difference_update({name})
    await state.update_data(selected_arrangements=selected)
    await callback.message.edit_reply_markup(
        reply_markup=work_arrangement_keyboard(selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.arrangements, F.data == "arr_done")
async def on_edit_arr_done(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User, lang: str
) -> None:
    data = await state.get_data()
    selected_names: set[str] = data.get("selected_arrangements", set())

    await session.execute(
        delete(UserWorkArrangement).where(UserWorkArrangement.user_id == db_user.id)
    )
    arrs = {
        a.name: a.id for a in (await session.execute(select(WorkArrangement))).scalars().all()
    }
    for name in selected_names:
        if name in arrs:
            session.add(UserWorkArrangement(user_id=db_user.id, arrangement_id=arrs[name]))

    await state.set_state(EditPrefState.choosing)
    updated = "Jenis kerja diperbarui! ✅" if lang == "id" else "Work arrangements updated! ✅"
    await callback.message.edit_text(
        f"{updated}\n\n{'Apa lagi?' if lang == 'id' else 'Anything else?'}",
        reply_markup=edit_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(EditPrefState.choosing, F.data == "edit_sal")
async def on_edit_salary(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(EditPrefState.salary)
    await callback.message.edit_text(
        t("ask_salary", lang), reply_markup=salary_keyboard(lang=lang)
    )
    await callback.answer()


@router.callback_query(EditPrefState.salary, F.data.startswith("sal:"))
async def on_edit_sal_select(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, db_user: User, lang: str
) -> None:
    from jobly.constants.levels import SALARY_RANGES

    slug = callback.data.split(":")[1]
    salary_min = salary_max = None
    for sr in SALARY_RANGES:
        if sr["slug"] == slug:
            salary_min = sr["min"]
            salary_max = sr["max"]
            break

    if db_user.preferences:
        db_user.preferences.salary_min = salary_min
        db_user.preferences.salary_max = salary_max
    else:
        session.add(UserPreference(user_id=db_user.id, salary_min=salary_min, salary_max=salary_max))

    await state.set_state(EditPrefState.choosing)
    updated = "Gaji diperbarui! ✅" if lang == "id" else "Salary updated! ✅"
    await callback.message.edit_text(
        f"{updated}\n\n{'Apa lagi?' if lang == 'id' else 'Anything else?'}",
        reply_markup=edit_menu_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(EditPrefState.choosing, F.data == "edit_done")
async def on_edit_done(callback: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.clear()
    done_msg = "Preferensi disimpan! ✅" if lang == "id" else "Preferences saved! ✅"
    await callback.message.edit_text(done_msg)
    await callback.answer()
