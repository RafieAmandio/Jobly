import logging

from sqlalchemy.ext.asyncio import AsyncSession

from jobly.models.cv import CV
from jobly.models.job import Job
from jobly.models.notification import TailoringHistory
from jobly.models.user import User
from jobly.services.ai import generate_cover_letter_content
from jobly.services.doc_generator import generate_cover_letter_docx, generate_cover_letter_pdf

logger = logging.getLogger(__name__)


async def generate_cover_letter(
    session: AsyncSession,
    user: User,
    cv: CV,
    job: Job,
    lang: str = "id",
) -> dict[str, bytes] | None:
    content = await generate_cover_letter_content(
        cv_text=cv.raw_text,
        job_description=job.description or "",
        job_title=job.title,
        company=job.company or "",
        lang=lang,
    )
    if not content:
        return None

    contact = {"email": user.email, "phone": user.phone}
    docx_bytes = generate_cover_letter_docx(content, user.full_name, contact)
    pdf_bytes = generate_cover_letter_pdf(content, user.full_name, contact)

    history = TailoringHistory(
        user_id=user.id,
        job_id=job.id,
        type="cover_letter",
        ai_response=content,
    )
    session.add(history)

    result = {"docx": docx_bytes}
    if pdf_bytes:
        result["pdf"] = pdf_bytes
    return result
