import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession

from jobly.models.cv import CV
from jobly.models.job import Job
from jobly.models.notification import TailoringHistory
from jobly.models.user import User
from jobly.services.ai import generate_cover_letter_content
from jobly.services.doc_generator import generate_cover_letter_docx, generate_cover_letter_pdf

logger = logging.getLogger(__name__)


def _candidate_level(user: User) -> str | None:
    return user.preferences.experience_level if user.preferences else None


def _formal_subject(job_title: str, company: str, lang: str) -> str:
    if lang == "id":
        return f"Perihal: Lamaran {job_title} - {company}" if company else f"Perihal: Lamaran {job_title}"
    return f"Subject: Application for {job_title} at {company}" if company else f"Subject: Application for {job_title}"


def _formal_recipient(company: str, lang: str) -> str:
    if lang == "id":
        return f"Yth. HRD {company}" if company else "Yth. Tim Rekrutmen"
    return f"Dear Hiring Manager at {company}," if company else "Dear Hiring Manager,"


def apply_cover_letter_rules(content: str, job: Job, lang: str = "id", signer_name: str | None = None) -> str:
    cleaned = (content or "").replace("\r\n", "\n").strip()
    if not cleaned:
        return ""

    paragraphs = [
        re.sub(r"\s+", " ", block.strip())
        for block in re.split(r"\n\s*\n", cleaned)
        if block.strip()
    ]
    paragraphs = [re.sub(r"^[\-•*]\s*", "", paragraph) for paragraph in paragraphs]

    subject_prefixes = ("subject:", "perihal:")
    recipient_prefixes = ("yth.", "dear ")

    if not paragraphs or not paragraphs[0].lower().startswith(subject_prefixes):
        paragraphs.insert(0, _formal_subject(job.title, job.company or "", lang))

    recipient_idx = 1 if paragraphs else 0
    if len(paragraphs) <= recipient_idx or not paragraphs[recipient_idx].lower().startswith(recipient_prefixes):
        paragraphs.insert(recipient_idx, _formal_recipient(job.company or "", lang))

    if lang == "id":
        closing = "Hormat saya,"
        disallowed_closings = ("best regards", "sincerely", "warm regards", "kind regards")
    else:
        closing = "Sincerely,"
        disallowed_closings = ("hormat saya",)

    closing_markers = (*disallowed_closings, closing.lower())
    has_closing = any(
        marker in paragraph.lower() for paragraph in paragraphs[-2:] for marker in closing_markers
    )
    if not has_closing:
        paragraphs.extend([closing, signer_name or "[Nama Kandidat]"])

    return "\n\n".join(paragraphs)


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
        candidate_level=_candidate_level(user),
    )
    if not content:
        return None

    content = apply_cover_letter_rules(content, job, lang, user.full_name)

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
