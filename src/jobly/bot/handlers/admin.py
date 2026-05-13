from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.bot.filters.admin import IsAdmin
from jobly.models.credit import CreditTransaction, Payment
from jobly.models.job import Job
from jobly.models.notification import TailoringHistory
from jobly.models.user import User

router = Router()
router.message.filter(IsAdmin())


@router.message(Command("admin"))
async def cmd_admin(message: Message) -> None:
    await message.answer(
        "🔧 Admin Commands:\n\n"
        "/stats — User & revenue stats\n"
        "/scraper_health — Check scraper status\n"
        "/give_credits <telegram_id> <amount> — Add credits\n"
        "/broadcast <message> — Send to all users\n"
        "/user_info <telegram_id> — View user details"
    )


@router.message(Command("stats"))
async def cmd_stats(message: Message, session: AsyncSession) -> None:
    total_users = (await session.execute(select(func.count(User.id)))).scalar() or 0
    active_users = (
        await session.execute(
            select(func.count(User.id)).where(User.is_active == True, User.onboarding_completed == True)
        )
    ).scalar() or 0
    total_jobs = (await session.execute(select(func.count(Job.id)))).scalar() or 0
    active_jobs = (
        await session.execute(select(func.count(Job.id)).where(Job.is_active == True))
    ).scalar() or 0
    total_tailors = (
        await session.execute(
            select(func.count(TailoringHistory.id)).where(TailoringHistory.type == "cv")
        )
    ).scalar() or 0
    total_covers = (
        await session.execute(
            select(func.count(TailoringHistory.id)).where(TailoringHistory.type == "cover_letter")
        )
    ).scalar() or 0
    total_revenue = (
        await session.execute(
            select(func.sum(Payment.amount_idr)).where(Payment.status == "paid")
        )
    ).scalar() or 0
    paid_payments = (
        await session.execute(select(func.count(Payment.id)).where(Payment.status == "paid"))
    ).scalar() or 0

    await message.answer(
        f"📊 Jobly Stats\n\n"
        f"👥 Users: {total_users} total, {active_users} active\n"
        f"💼 Jobs: {total_jobs} total, {active_jobs} active\n"
        f"📄 CV Tailored: {total_tailors}\n"
        f"✉️ Cover Letters: {total_covers}\n"
        f"💰 Revenue: Rp {total_revenue:,}\n"
        f"🧾 Payments: {paid_payments} completed"
    )


@router.message(Command("scraper_health"))
async def cmd_scraper_health(message: Message) -> None:
    from jobly.scrapers.registry import registry

    statuses = await registry.health_check_all()
    if not statuses:
        await message.answer("No scrapers registered.")
        return

    lines = ["🔍 Scraper Health:\n"]
    for name, healthy in statuses.items():
        icon = "✅" if healthy else "❌"
        lines.append(f"{icon} {name}")
    await message.answer("\n".join(lines))


@router.message(Command("give_credits"))
async def cmd_give_credits(message: Message, session: AsyncSession) -> None:
    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Usage: /give_credits <telegram_id> <amount>")
        return

    try:
        telegram_id = int(parts[1])
        amount = int(parts[2])
    except ValueError:
        await message.answer("Invalid telegram_id or amount.")
        return

    from jobly.services.user import get_user_by_telegram_id
    from jobly.services.credit import add_credit

    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        await message.answer(f"User {telegram_id} not found.")
        return

    new_balance = await add_credit(
        session, user, amount, "admin_adjustment",
        description=f"Admin adjustment by {message.from_user.id}",
    )
    await message.answer(f"✅ Added {amount} credits to {user.full_name}. Balance: {new_balance}")


@router.message(Command("user_info"))
async def cmd_user_info(message: Message, session: AsyncSession) -> None:
    parts = message.text.split()
    if len(parts) != 2:
        await message.answer("Usage: /user_info <telegram_id>")
        return

    try:
        telegram_id = int(parts[1])
    except ValueError:
        await message.answer("Invalid telegram_id.")
        return

    from jobly.services.user import get_user_by_telegram_id

    user = await get_user_by_telegram_id(session, telegram_id)
    if not user:
        await message.answer(f"User {telegram_id} not found.")
        return

    tailors = (
        await session.execute(
            select(func.count(TailoringHistory.id)).where(TailoringHistory.user_id == user.id)
        )
    ).scalar() or 0

    await message.answer(
        f"👤 User Info\n\n"
        f"Name: {user.full_name}\n"
        f"Telegram: @{user.telegram_username or 'N/A'} ({user.telegram_id})\n"
        f"Email: {user.email or 'N/A'}\n"
        f"Language: {user.language}\n"
        f"Credits: {user.credit_balance}\n"
        f"Onboarded: {'✅' if user.onboarding_completed else '❌'}\n"
        f"Active: {'✅' if user.is_active else '❌'}\n"
        f"Tailorings: {tailors}\n"
        f"Referral: {user.referral_code}\n"
        f"Joined: {user.created_at.strftime('%Y-%m-%d %H:%M')}"
    )


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, session: AsyncSession) -> None:
    text = message.text.removeprefix("/broadcast").strip()
    if not text:
        await message.answer("Usage: /broadcast <message>")
        return

    users = (
        await session.execute(
            select(User).where(User.is_active == True, User.onboarding_completed == True)
        )
    ).scalars().all()

    sent = 0
    failed = 0
    for user in users:
        try:
            await message.bot.send_message(chat_id=user.telegram_id, text=text)
            sent += 1
        except Exception:
            failed += 1

    await message.answer(f"📢 Broadcast complete: {sent} sent, {failed} failed")
