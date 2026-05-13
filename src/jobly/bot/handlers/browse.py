from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.bot.keyboards.jobs import job_card_keyboard
from jobly.i18n.strings import t
from jobly.models.job import Job, JobCategory
from jobly.models.notification import NotificationLog
from jobly.models.user import User, UserCategory
from jobly.services.notification import format_job_card

router = Router()

MAX_BROWSE_RESULTS = 5


@router.message(Command("browse"))
async def cmd_browse(
    message: Message, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    user_cat_ids = (
        await session.execute(
            select(UserCategory.category_id).where(UserCategory.user_id == db_user.id)
        )
    ).scalars().all()

    if not user_cat_ids:
        no_prefs = (
            "Kamu belum memilih kategori pekerjaan. Gunakan /edit_preferences."
            if lang == "id"
            else "You haven't selected any job categories. Use /edit_preferences."
        )
        await message.answer(no_prefs)
        return

    already_seen = (
        await session.execute(
            select(NotificationLog.job_id).where(NotificationLog.user_id == db_user.id)
        )
    ).scalars().all()

    matching_job_ids = (
        await session.execute(
            select(JobCategory.job_id)
            .where(JobCategory.category_id.in_(user_cat_ids))
            .distinct()
        )
    ).scalars().all()

    query = (
        select(Job)
        .where(
            Job.id.in_(matching_job_ids),
            Job.is_active == True,
        )
        .order_by(Job.scraped_at.desc())
        .limit(MAX_BROWSE_RESULTS)
    )
    if already_seen:
        query = query.where(Job.id.not_in(already_seen))

    jobs = (await session.execute(query)).scalars().all()

    if not jobs:
        no_jobs = (
            "Belum ada lowongan yang cocok saat ini. Coba lagi nanti!"
            if lang == "id"
            else "No matching jobs found right now. Check back later!"
        )
        await message.answer(no_jobs)
        return

    header = f"💼 {len(jobs)} lowongan terbaru:" if lang == "id" else f"💼 {len(jobs)} latest jobs:"
    await message.answer(header)

    for job in jobs:
        text = format_job_card(job, lang)
        keyboard = job_card_keyboard(str(job.id), job.url, lang)
        await message.answer(text, reply_markup=keyboard)


@router.message(Command("history"))
async def cmd_history(
    message: Message, session: AsyncSession, db_user: User | None, lang: str
) -> None:
    if not db_user:
        await message.answer(t("not_registered", lang))
        return

    from jobly.models.notification import TailoringHistory

    history = (
        await session.execute(
            select(TailoringHistory)
            .where(TailoringHistory.user_id == db_user.id)
            .order_by(TailoringHistory.created_at.desc())
            .limit(10)
        )
    ).scalars().all()

    if not history:
        no_hist = (
            "Belum ada riwayat tailoring." if lang == "id" else "No tailoring history yet."
        )
        await message.answer(no_hist)
        return

    lines = ["📜 Riwayat Tailoring:\n" if lang == "id" else "📜 Tailoring History:\n"]
    for h in history:
        date_str = h.created_at.strftime("%d/%m/%Y %H:%M")
        type_label = "CV" if h.type == "cv" else "Cover Letter"
        job = await session.get(Job, h.job_id) if h.job_id else None
        job_label = f"{job.title} @ {job.company}" if job else "N/A"
        lines.append(f"• {date_str} — {type_label} — {job_label}")

    await message.answer("\n".join(lines))
