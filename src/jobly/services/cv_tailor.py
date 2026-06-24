import logging

from sqlalchemy.ext.asyncio import AsyncSession

from jobly.models.cv import CV
from jobly.models.job import Job
from jobly.models.notification import TailoringHistory
from jobly.models.user import User
from jobly.services.ai import tailor_cv_content
from jobly.services.doc_generator import generate_cv_docx, generate_cv_pdf

logger = logging.getLogger(__name__)


async def tailor_cv(
    session: AsyncSession,
    user: User,
    cv: CV,
    job: Job,
    lang: str = "id",
) -> dict[str, bytes] | None:
    tailored_data = await tailor_cv_content(
        cv_text=cv.raw_text,
        job_description=job.description or "",
        job_title=job.title,
        company=job.company or "",
        lang=lang,
    )
    if not tailored_data:
        return None

    # Fall back to the user record for any contact field the AI didn't extract.
    contact = dict(tailored_data.get("contact") or {})
    if not contact.get("email") and user.email:
        contact["email"] = user.email
    if not contact.get("phone") and user.phone:
        contact["phone"] = user.phone
    tailored_data["contact"] = contact

    docx_bytes = generate_cv_docx(tailored_data, user.full_name)
    pdf_bytes = generate_cv_pdf(tailored_data, user.full_name)

    history = TailoringHistory(
        user_id=user.id,
        job_id=job.id,
        type="cv",
        ai_response=str(tailored_data),
    )
    session.add(history)

    result = {"docx": docx_bytes}
    if pdf_bytes:
        result["pdf"] = pdf_bytes
    return result
