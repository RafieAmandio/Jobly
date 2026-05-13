import logging

from aiogram import Bot
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.bot.keyboards.jobs import job_card_keyboard
from jobly.models.job import Job
from jobly.models.notification import NotificationLog
from jobly.models.user import User

logger = logging.getLogger(__name__)


def format_job_card(job: Job, lang: str = "id") -> str:
    salary = ""
    if job.salary_text:
        salary = f"\n💰 {job.salary_text}"
    elif job.salary_min and job.salary_max:
        salary = f"\n💰 Rp {job.salary_min:,} - Rp {job.salary_max:,}/bulan"

    arrangement = ""
    if job.work_arrangement:
        arrangement = f" ({job.work_arrangement})"

    location = job.location or ("Tidak disebutkan" if lang == "id" else "Not specified")
    source = job.source.capitalize()

    return (
        f"🏢 {job.title} — {job.company or 'Unknown'}\n"
        f"📍 {location}{arrangement}"
        f"{salary}\n"
        f"🔗 Source: {source}"
    )


async def send_job_notification(
    bot: Bot,
    session: AsyncSession,
    user: User,
    job: Job,
) -> bool:
    try:
        text = format_job_card(job, user.language)
        keyboard = job_card_keyboard(str(job.id), job.url, user.language)

        message = await bot.send_message(
            chat_id=user.telegram_id,
            text=text,
            reply_markup=keyboard,
        )

        log = NotificationLog(
            user_id=user.id,
            job_id=job.id,
            message_id=message.message_id,
        )
        session.add(log)
        return True
    except Exception:
        logger.exception(f"Failed to notify user {user.telegram_id} about job {job.id}")
        return False
