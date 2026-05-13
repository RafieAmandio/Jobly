from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.bot.keyboards.jobs import topup_keyboard
from jobly.constants.levels import CREDIT_PACKAGES
from jobly.i18n.strings import t
from jobly.models.user import User
from jobly.services.credit import get_transaction_history

router = Router()


@router.message(Command("credits"))
async def cmd_credits(message: Message, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return
    await message.answer(t("credits_balance", lang, balance=db_user.credit_balance))


@router.message(Command("topup"))
async def cmd_topup(message: Message, db_user: User | None, lang: str) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return
    await message.answer(t("topup_menu", lang), reply_markup=topup_keyboard())


@router.callback_query(F.data.startswith("topup:"))
async def on_topup(callback: CallbackQuery, session: AsyncSession, db_user: User | None, lang: str) -> None:
    if not db_user:
        await callback.answer()
        return

    package_name = callback.data.split(":")[1]
    package = next((p for p in CREDIT_PACKAGES if p["name"] == package_name), None)
    if not package:
        await callback.answer("Invalid package")
        return

    from jobly.services.payment import create_xendit_invoice

    invoice_url = await create_xendit_invoice(
        session=session,
        user=db_user,
        package=package,
    )

    if invoice_url:
        await callback.message.answer(t("payment_created", lang, url=invoice_url))
    else:
        error = "Gagal membuat invoice." if lang == "id" else "Failed to create invoice."
        await callback.message.answer(error)
    await callback.answer()


@router.message(Command("transactions"))
async def cmd_transactions(
    message: Message, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    txs = await get_transaction_history(session, db_user)
    if not txs:
        no_tx = "Belum ada transaksi." if lang == "id" else "No transactions yet."
        await message.answer(no_tx)
        return

    lines = ["📊 Riwayat Transaksi:\n" if lang == "id" else "📊 Transaction History:\n"]
    for tx in txs:
        sign = "+" if tx.amount > 0 else ""
        date_str = tx.created_at.strftime("%d/%m/%Y %H:%M")
        desc = tx.description or tx.type
        lines.append(f"{date_str} | {sign}{tx.amount} | {desc} | Saldo: {tx.balance_after}")

    await message.answer("\n".join(lines))
