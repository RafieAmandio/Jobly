from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def job_card_keyboard(job_id: str, job_url: str, lang: str = "id") -> InlineKeyboardMarkup:
    if lang == "id":
        return InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📄 Sesuaikan CV — 1 kredit", callback_data=f"tailor:{job_id}"
                ),
                InlineKeyboardButton(
                    text="✉️ Cover Letter — 1 kredit", callback_data=f"cover:{job_id}"
                ),
            ],
            [
                InlineKeyboardButton(text="🔗 Lihat Asli", url=job_url),
            ],
        ])
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📄 Tailor CV — 1 credit", callback_data=f"tailor:{job_id}"
            ),
            InlineKeyboardButton(
                text="✉️ Cover Letter — 1 credit", callback_data=f"cover:{job_id}"
            ),
        ],
        [
            InlineKeyboardButton(text="🔗 View Original", url=job_url),
        ],
    ])


def topup_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Starter — 5 kredit — Rp 25.000", callback_data="topup:starter")],
        [InlineKeyboardButton(text="🔥 Popular — 15 kredit — Rp 60.000", callback_data="topup:popular")],
        [InlineKeyboardButton(text="💎 Pro — 50 kredit — Rp 150.000", callback_data="topup:pro")],
        [InlineKeyboardButton(text="👑 Bulk — 100 kredit — Rp 250.000", callback_data="topup:bulk")],
    ])
