import logging
import re

from sqlalchemy.ext.asyncio import AsyncSession

from jobly.models.cv import CV
from jobly.models.job import Job
from jobly.models.notification import TailoringHistory
from jobly.models.user import User
from jobly.services.ai import tailor_cv_content
from jobly.services.doc_generator import generate_cv_docx, generate_cv_pdf

logger = logging.getLogger(__name__)


def _normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"\D+", "", phone)
    if not digits:
        return None
    if digits.startswith("62"):
        return f"+{digits}"
    if digits.startswith("0"):
        return f"+62{digits[1:]}"
    return f"+62{digits}"


def _trim_location(location: str | None) -> str | None:
    if not location:
        return None
    return location.split(",", 1)[0].strip()


def _limit_bullets(items: list[dict] | None, org_key: str) -> list[dict]:
    normalized = []
    for item in items or []:
        bullets = [str(b).strip() for b in item.get("bullets", []) if str(b).strip()][:3]
        normalized.append(
            {
                org_key: item.get(org_key, ""),
                "title": item.get("title", ""),
                "period": item.get("period", ""),
                "bullets": bullets,
                "brief": item.get("brief", ""),
            }
        )
    return normalized


def apply_cv_rules(tailored_data: dict, user: User) -> dict:
    normalized = dict(tailored_data or {})

    contact = dict(normalized.get("contact") or {})
    if not contact.get("email") and user.email:
        contact["email"] = user.email
    phone = _normalize_phone(contact.get("phone") or user.phone)
    if phone:
        contact["phone"] = phone
    location = _trim_location(contact.get("location"))
    if location:
        contact["location"] = location
    portfolio = contact.get("portfolio") or contact.get("linkedin")
    if portfolio:
        contact["portfolio"] = str(portfolio).strip()
    normalized["contact"] = contact

    normalized["experience"] = _limit_bullets(normalized.get("experience"), "company")
    normalized["leadership"] = _limit_bullets(normalized.get("leadership"), "organization")

    extra_miles = []
    for key in ("awards", "projects", "certifications", "extra_miles"):
        for item in normalized.get(key, []) or []:
            text = str(item).strip()
            if text and text not in extra_miles:
                extra_miles.append(text)
    normalized["extra_miles"] = extra_miles

    skills = normalized.get("skills") or {}
    if isinstance(skills, list):
        normalized["skills"] = {
            "technical": [str(item).strip() for item in skills if str(item).strip()],
            "soft": [],
            "tools": [],
        }
    else:
        normalized["skills"] = {
            "technical": [str(item).strip() for item in skills.get("technical", []) if str(item).strip()],
            "soft": [str(item).strip() for item in skills.get("soft", []) if str(item).strip()],
            "tools": [str(item).strip() for item in skills.get("tools", []) if str(item).strip()],
        }

    return normalized


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

    tailored_data = apply_cv_rules(tailored_data, user)

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
