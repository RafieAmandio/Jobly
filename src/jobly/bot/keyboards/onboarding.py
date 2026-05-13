from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from jobly.constants.categories import CATEGORIES
from jobly.constants.levels import EXPERIENCE_LEVELS, SALARY_RANGES, WORK_ARRANGEMENTS
from jobly.constants.locations import LOCATIONS

ITEMS_PER_PAGE = 8


def language_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇮🇩 Bahasa Indonesia", callback_data="lang:id"),
            InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
        ]
    ])


def category_keyboard(
    page: int = 0, selected: set[int] | None = None, lang: str = "id"
) -> InlineKeyboardMarkup:
    selected = selected or set()
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = CATEGORIES[start:end]
    total_pages = (len(CATEGORIES) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    rows: list[list[InlineKeyboardButton]] = []
    for i, cat in enumerate(page_items, start=start):
        label = cat["name_id"] if lang == "id" else cat["name_en"]
        check = "✅ " if i in selected else ""
        rows.append([
            InlineKeyboardButton(text=f"{check}{label}", callback_data=f"cat:{i}")
        ])

    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"cat_page:{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if end < len(CATEGORIES):
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"cat_page:{page + 1}"))
    rows.append(nav_row)

    if selected:
        rows.append([
            InlineKeyboardButton(text=f"✅ Selesai ({len(selected)} dipilih)", callback_data="cat_done")
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def experience_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for lvl in EXPERIENCE_LEVELS:
        label = lvl["label_id"] if lang == "id" else lvl["label_en"]
        rows.append([InlineKeyboardButton(text=label, callback_data=f"exp:{lvl['slug']}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def location_keyboard(
    page: int = 0, selected: set[int] | None = None, lang: str = "id"
) -> InlineKeyboardMarkup:
    selected = selected or set()
    start = page * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    page_items = LOCATIONS[start:end]
    total_pages = (len(LOCATIONS) + ITEMS_PER_PAGE - 1) // ITEMS_PER_PAGE

    rows: list[list[InlineKeyboardButton]] = []
    for i, loc in enumerate(page_items, start=start):
        region = f" ({loc['region']})" if loc["region"] else ""
        check = "✅ " if i in selected else ""
        rows.append([
            InlineKeyboardButton(text=f"{check}{loc['city']}{region}", callback_data=f"loc:{i}")
        ])

    nav_row: list[InlineKeyboardButton] = []
    if page > 0:
        nav_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"loc_page:{page - 1}"))
    nav_row.append(InlineKeyboardButton(text=f"{page + 1}/{total_pages}", callback_data="noop"))
    if end < len(LOCATIONS):
        nav_row.append(InlineKeyboardButton(text="➡️", callback_data=f"loc_page:{page + 1}"))
    rows.append(nav_row)

    if selected:
        rows.append([
            InlineKeyboardButton(text=f"✅ Selesai ({len(selected)} dipilih)", callback_data="loc_done")
        ])

    return InlineKeyboardMarkup(inline_keyboard=rows)


def work_arrangement_keyboard(
    selected: set[str] | None = None, lang: str = "id"
) -> InlineKeyboardMarkup:
    selected = selected or set()
    rows: list[list[InlineKeyboardButton]] = []
    for arr in WORK_ARRANGEMENTS:
        label = arr["label_id"] if lang == "id" else arr["label_en"]
        check = "✅ " if arr["name"] in selected else ""
        rows.append([
            InlineKeyboardButton(text=f"{check}{label}", callback_data=f"arr:{arr['name']}")
        ])
    if selected:
        rows.append([
            InlineKeyboardButton(text=f"✅ Selesai ({len(selected)} dipilih)", callback_data="arr_done")
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def salary_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = []
    for sr in SALARY_RANGES:
        rows.append([InlineKeyboardButton(text=sr["label"], callback_data=f"sal:{sr['slug']}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def confirm_keyboard(lang: str = "id") -> InlineKeyboardMarkup:
    if lang == "id":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Konfirmasi", callback_data="onboard_confirm"),
                InlineKeyboardButton(text="🔄 Ulangi", callback_data="onboard_restart"),
            ]
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Confirm", callback_data="onboard_confirm"),
            InlineKeyboardButton(text="🔄 Start Over", callback_data="onboard_restart"),
        ]
    ])
