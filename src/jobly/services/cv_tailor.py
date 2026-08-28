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

MAX_SUMMARY_CHARS = 450
MAX_EXPERIENCE_ITEMS = 4
MAX_LEADERSHIP_ITEMS = 2
MAX_EXTRA_MILES_ITEMS = 5
MAX_SKILLS_PER_GROUP = 8
ACTIVE_VERB_PATTERN = re.compile(
    r"^(Led|Built|Created|Drove|Delivered|Launched|Managed|Owned|Improved|Increased|Reduced|Optimized|Developed|Designed|Implemented|Generated|Scaled|Coordinated|Executed|Produced|Supported|Analyzed|Streamlined|Boosted|Expanded|Achieved|Negotiated|Spearheaded|Established|Automated|Revamped|Accelerated|Strengthened|Secured|Collaborated|Directed|Facilitated|Resolved|Maintained|Initiated|Presented|Mentored)\b",
    re.IGNORECASE,
)


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


def _trim_text(text: str | None, max_chars: int) -> str:
    cleaned = str(text or "").strip()
    if len(cleaned) <= max_chars:
        return cleaned
    trimmed = cleaned[:max_chars].rsplit(" ", 1)[0].strip()
    return trimmed or cleaned[:max_chars].strip()


def _ensure_active_verb(bullet: str) -> str:
    cleaned = re.sub(r"^[\-•\s]+", "", str(bullet or "")).strip()
    if not cleaned:
        return ""
    if ACTIVE_VERB_PATTERN.match(cleaned):
        return cleaned
    return f"Delivered {cleaned[0].lower() + cleaned[1:] if len(cleaned) > 1 else cleaned.lower()}"


def _prioritize_keywords(items: list[str], keywords: list[str], limit: int) -> list[str]:
    scored = []
    lowered_keywords = [k.lower() for k in keywords if k]
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        hay = text.lower()
        score = sum(1 for k in lowered_keywords if k in hay)
        scored.append((score, text))
    scored.sort(key=lambda row: (-row[0], items.index(row[1]) if row[1] in items else 0))
    return [text for _, text in scored[:limit]]


def _limit_bullets(items: list[dict] | None, org_key: str) -> list[dict]:
    normalized = []
    for item in items or []:
        bullets = [_ensure_active_verb(b) for b in item.get("bullets", [])]
        bullets = [b for b in bullets if b][:3]
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


def _extract_keywords(job_title: str, company: str, job_description: str) -> list[str]:
    source = f"{job_title} {company} {job_description}"
    candidates = re.findall(r"[A-Za-z][A-Za-z0-9+.#/-]{2,}", source)
    stop = {
        "and", "the", "for", "with", "that", "this", "from", "your", "you", "our", "are", "job", "role",
        "will", "have", "has", "not", "but", "all", "can", "work", "team", "using", "use", "per", "year",
        "years", "experience", "skills", "skill", "requirements", "about", "into", "within", "their", "they",
        "kami", "dan", "yang", "untuk", "dengan", "dari", "atau", "pada", "akan", "the", "company",
    }
    seen = set()
    keywords = []
    for token in candidates:
        low = token.lower()
        if low in stop or low in seen:
            continue
        seen.add(low)
        keywords.append(token)
        if len(keywords) >= 20:
            break
    return keywords


def apply_cv_rules(
    tailored_data: dict,
    user: User,
    *,
    job_title: str = "",
    company: str = "",
    job_description: str = "",
) -> dict:
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

    keywords = _extract_keywords(job_title, company, job_description)
    normalized["summary"] = _trim_text(normalized.get("summary"), MAX_SUMMARY_CHARS)
    normalized["experience"] = _limit_bullets(normalized.get("experience"), "company")[:MAX_EXPERIENCE_ITEMS]
    normalized["leadership"] = _limit_bullets(normalized.get("leadership"), "organization")[:MAX_LEADERSHIP_ITEMS]

    extra_miles = []
    for key in ("awards", "projects", "certifications", "extra_miles"):
        for item in normalized.get(key, []) or []:
            text = str(item).strip()
            if text and text not in extra_miles:
                extra_miles.append(text)
    normalized["extra_miles"] = _prioritize_keywords(extra_miles, keywords, MAX_EXTRA_MILES_ITEMS)

    skills = normalized.get("skills") or {}
    if isinstance(skills, list):
        normalized["skills"] = {
            "technical": [str(item).strip() for item in skills if str(item).strip()][:MAX_SKILLS_PER_GROUP],
            "soft": [],
            "tools": [],
        }
    else:
        normalized["skills"] = {
            "technical": _prioritize_keywords(
                [str(item).strip() for item in skills.get("technical", []) if str(item).strip()],
                keywords,
                MAX_SKILLS_PER_GROUP,
            ),
            "soft": _prioritize_keywords(
                [str(item).strip() for item in skills.get("soft", []) if str(item).strip()],
                keywords,
                MAX_SKILLS_PER_GROUP,
            ),
            "tools": _prioritize_keywords(
                [str(item).strip() for item in skills.get("tools", []) if str(item).strip()],
                keywords,
                MAX_SKILLS_PER_GROUP,
            ),
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

    tailored_data = apply_cv_rules(
        tailored_data,
        user,
        job_title=job.title,
        company=job.company or "",
        job_description=job.description or "",
    )

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
