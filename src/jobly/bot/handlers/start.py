from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.bot.keyboards.onboarding import (
    category_keyboard,
    confirm_keyboard,
    experience_keyboard,
    language_keyboard,
    location_keyboard,
    salary_keyboard,
    work_arrangement_keyboard,
)
from jobly.bot.states.onboarding import OnboardingState
from jobly.constants.categories import CATEGORIES
from jobly.constants.levels import EXPERIENCE_LEVELS
from jobly.constants.locations import LOCATIONS
from jobly.i18n.strings import t
from jobly.models.user import User
from jobly.services.user import create_user, get_user_by_telegram_id, save_preferences

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, session: AsyncSession) -> None:
    user = await get_user_by_telegram_id(session, message.from_user.id)
    if user and user.onboarding_completed:
        await message.answer(t("already_registered", user.language))
        return

    await state.set_state(OnboardingState.language)
    await message.answer(
        "Selamat datang di Jobly! / Welcome to Jobly!\n\nPilih bahasa / Choose language:",
        reply_markup=language_keyboard(),
    )


@router.callback_query(OnboardingState.language, F.data.startswith("lang:"))
async def on_language(callback: CallbackQuery, state: FSMContext) -> None:
    lang = callback.data.split(":")[1]
    await state.update_data(language=lang)
    await state.set_state(OnboardingState.name)
    await callback.message.edit_text(t("ask_name", lang))
    await callback.answer()


@router.message(OnboardingState.name)
async def on_name(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    await state.update_data(full_name=message.text.strip())
    await state.set_state(OnboardingState.email)
    await message.answer(t("ask_email", lang))


@router.message(OnboardingState.email)
async def on_email(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    await state.update_data(email=message.text.strip())
    await state.set_state(OnboardingState.phone)
    await message.answer(t("ask_phone", lang))


@router.message(OnboardingState.phone, Command("skip"))
async def on_phone_skip(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    await state.update_data(phone=None, selected_categories=[])
    await state.set_state(OnboardingState.categories)
    await message.answer(
        t("ask_categories", lang),
        reply_markup=category_keyboard(page=0, lang=lang),
    )


@router.message(OnboardingState.phone)
async def on_phone(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")

    phone = message.text.strip() if message.text else None
    await state.update_data(phone=phone, selected_categories=[])
    await state.set_state(OnboardingState.categories)
    await message.answer(
        t("ask_categories", lang),
        reply_markup=category_keyboard(page=0, lang=lang),
    )


@router.callback_query(OnboardingState.categories, F.data.startswith("cat:"))
async def on_category_select(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    idx = int(callback.data.split(":")[1])
    selected: list[int] = data.get("selected_categories", [])

    if idx in selected:
        selected.remove(idx)
    else:
        selected.append(idx)
    await state.update_data(selected_categories=selected)

    current_page = data.get("cat_page", 0)
    await callback.message.edit_reply_markup(
        reply_markup=category_keyboard(page=current_page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(OnboardingState.categories, F.data.startswith("cat_page:"))
async def on_category_page(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    page = int(callback.data.split(":")[1])
    selected: list[int] = data.get("selected_categories", [])
    await state.update_data(cat_page=page)
    await callback.message.edit_reply_markup(
        reply_markup=category_keyboard(page=page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(OnboardingState.categories, F.data == "cat_done")
async def on_category_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    await state.set_state(OnboardingState.experience)
    await callback.message.edit_text(
        t("ask_experience", lang),
        reply_markup=experience_keyboard(lang=lang),
    )
    await callback.answer()


@router.callback_query(OnboardingState.experience, F.data.startswith("exp:"))
async def on_experience(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    slug = callback.data.split(":")[1]
    await state.update_data(experience_level=slug, selected_locations=[])
    await state.set_state(OnboardingState.locations)
    await callback.message.edit_text(
        t("ask_locations", lang),
        reply_markup=location_keyboard(page=0, lang=lang),
    )
    await callback.answer()


@router.callback_query(OnboardingState.locations, F.data.startswith("loc:"))
async def on_location_select(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    idx = int(callback.data.split(":")[1])
    selected: list[int] = data.get("selected_locations", [])

    if idx in selected:
        selected.remove(idx)
    else:
        selected.append(idx)
    await state.update_data(selected_locations=selected)

    current_page = data.get("loc_page", 0)
    await callback.message.edit_reply_markup(
        reply_markup=location_keyboard(page=current_page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(OnboardingState.locations, F.data.startswith("loc_page:"))
async def on_location_page(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    page = int(callback.data.split(":")[1])
    selected: list[int] = data.get("selected_locations", [])
    await state.update_data(loc_page=page)
    await callback.message.edit_reply_markup(
        reply_markup=location_keyboard(page=page, selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(OnboardingState.locations, F.data == "loc_done")
async def on_location_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    await state.update_data(selected_arrangements=[])
    await state.set_state(OnboardingState.work_arrangement)
    await callback.message.edit_text(
        t("ask_work_arrangement", lang),
        reply_markup=work_arrangement_keyboard(lang=lang),
    )
    await callback.answer()


@router.callback_query(OnboardingState.work_arrangement, F.data.startswith("arr:"))
async def on_arrangement_select(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    name = callback.data.split(":")[1]
    selected: list[str] = data.get("selected_arrangements", [])

    if name in selected:
        selected.remove(name)
    else:
        selected.append(name)
    await state.update_data(selected_arrangements=selected)
    await callback.message.edit_reply_markup(
        reply_markup=work_arrangement_keyboard(selected=selected, lang=lang)
    )
    await callback.answer()


@router.callback_query(OnboardingState.work_arrangement, F.data == "arr_done")
async def on_arrangement_done(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    await state.set_state(OnboardingState.salary)
    await callback.message.edit_text(
        t("ask_salary", lang),
        reply_markup=salary_keyboard(lang=lang),
    )
    await callback.answer()


@router.callback_query(OnboardingState.salary, F.data.startswith("sal:"))
async def on_salary(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    slug = callback.data.split(":")[1]
    await state.update_data(salary_slug=slug)
    await state.set_state(OnboardingState.cv_upload)
    await callback.message.edit_text(t("ask_cv", lang))
    await callback.answer()


@router.message(OnboardingState.cv_upload, F.document)
async def on_cv_pdf(message: Message, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")

    doc = message.document
    if doc.mime_type != "application/pdf":
        await message.answer("Please upload a PDF file." if lang == "en" else "Mohon upload file PDF.")
        return

    file = await message.bot.download(doc)
    pdf_bytes = file.read()

    from jobly.services.cv_parser import extract_text_from_pdf

    cv_text = extract_text_from_pdf(pdf_bytes)
    await state.update_data(cv_text=cv_text)
    await _show_confirmation(message, state, data, lang)


@router.message(OnboardingState.cv_upload, F.text)
async def on_cv_text(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")
    await state.update_data(cv_text=message.text.strip())
    await _show_confirmation(message, state, data, lang)


async def _show_confirmation(
    message: Message, state: FSMContext, data: dict, lang: str
) -> None:
    data = await state.get_data()
    selected_cats = data.get("selected_categories", [])
    cat_names = [
        CATEGORIES[i]["name_id" if lang == "id" else "name_en"] for i in selected_cats
    ]
    selected_locs = data.get("selected_locations", [])
    loc_names = [LOCATIONS[i]["city"] for i in selected_locs]

    exp_slug = data.get("experience_level", "")
    exp_label = exp_slug
    for lvl in EXPERIENCE_LEVELS:
        if lvl["slug"] == exp_slug:
            exp_label = lvl["label_id" if lang == "id" else "label_en"]
            break

    summary = t(
        "profile_summary",
        lang,
        name=data.get("full_name", ""),
        email=data.get("email", "-"),
        level=exp_label,
        categories=", ".join(cat_names) if cat_names else "-",
        locations=", ".join(loc_names) if loc_names else "-",
        arrangements=", ".join(data.get("selected_arrangements", [])),
        credits="3",
    )

    await state.set_state(OnboardingState.confirm)
    await message.answer(summary, reply_markup=confirm_keyboard(lang))


@router.callback_query(OnboardingState.confirm, F.data == "onboard_confirm")
async def on_confirm(callback: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    lang = data.get("language", "id")

    user = await create_user(
        session,
        telegram_id=callback.from_user.id,
        full_name=data["full_name"],
        email=data.get("email"),
        phone=data.get("phone"),
        language=lang,
        telegram_username=callback.from_user.username,
    )

    await save_preferences(
        session,
        user=user,
        experience_level=data["experience_level"],
        salary_slug=data.get("salary_slug"),
        category_indices=data.get("selected_categories", []),
        location_indices=data.get("selected_locations", []),
        arrangement_names=data.get("selected_arrangements", []),
    )

    from jobly.models.cv import CV

    cv = CV(user_id=user.id, raw_text=data.get("cv_text", ""))
    session.add(cv)

    await state.clear()
    await callback.message.edit_text(t("onboarding_complete", lang))
    await callback.answer()


@router.callback_query(OnboardingState.confirm, F.data == "onboard_restart")
async def on_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await state.set_state(OnboardingState.language)
    await callback.message.edit_text(
        "Pilih bahasa / Choose language:",
        reply_markup=language_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "noop")
async def on_noop(callback: CallbackQuery) -> None:
    await callback.answer()
