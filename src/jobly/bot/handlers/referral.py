from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.i18n.strings import t
from jobly.models.user import User
from jobly.services.credit import add_credit

router = Router()

REFERRAL_BONUS = 2


@router.message(Command("referral"))
async def cmd_referral(message: Message, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    if lang == "id":
        await message.answer(
            f"🎁 Program Referral\n\n"
            f"Kode referral kamu: <code>{db_user.referral_code}</code>\n\n"
            f"Bagikan kode ini ke teman. Ketika mereka mendaftar dan menyelesaikan "
            f"onboarding dengan kode kamu, kalian berdua mendapat {REFERRAL_BONUS} kredit gratis!\n\n"
            f"Cara pakai: Teman kamu ketik /start lalu gunakan /redeem {db_user.referral_code}"
        )
    else:
        await message.answer(
            f"🎁 Referral Program\n\n"
            f"Your referral code: <code>{db_user.referral_code}</code>\n\n"
            f"Share this code with friends. When they sign up and complete "
            f"onboarding with your code, you both get {REFERRAL_BONUS} free credits!\n\n"
            f"How to use: Your friend types /start then /redeem {db_user.referral_code}"
        )


@router.message(Command("redeem"))
async def cmd_redeem(
    message: Message, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    parts = message.text.split()
    if len(parts) != 2:
        usage = "Cara pakai: /redeem <kode>" if lang == "id" else "Usage: /redeem <code>"
        await message.answer(usage)
        return

    code = parts[1].strip().upper()

    if db_user.referral_code == code:
        own_code = (
            "Tidak bisa menggunakan kode sendiri." if lang == "id"
            else "You can't use your own referral code."
        )
        await message.answer(own_code)
        return

    if db_user.referred_by:
        already = (
            "Kamu sudah menggunakan kode referral." if lang == "id"
            else "You've already used a referral code."
        )
        await message.answer(already)
        return

    referrer = (
        await session.execute(select(User).where(User.referral_code == code))
    ).scalar_one_or_none()

    if not referrer:
        invalid = "Kode tidak valid." if lang == "id" else "Invalid referral code."
        await message.answer(invalid)
        return

    db_user.referred_by = referrer.id

    await add_credit(
        session, db_user, REFERRAL_BONUS, "referral",
        description=f"Referral bonus from {referrer.referral_code}",
    )
    await add_credit(
        session, referrer, REFERRAL_BONUS, "referral",
        description=f"Referral bonus: {db_user.full_name} joined",
    )

    if lang == "id":
        await message.answer(
            f"✅ Kode referral berhasil! Kamu dan {referrer.full_name} masing-masing mendapat "
            f"{REFERRAL_BONUS} kredit gratis."
        )
    else:
        await message.answer(
            f"✅ Referral code applied! You and {referrer.full_name} each received "
            f"{REFERRAL_BONUS} free credits."
        )

    try:
        notify_text = (
            f"🎉 {db_user.full_name} bergabung menggunakan kode referral kamu! "
            f"+{REFERRAL_BONUS} kredit."
        )
        await message.bot.send_message(chat_id=referrer.telegram_id, text=notify_text)
    except Exception:
        pass
