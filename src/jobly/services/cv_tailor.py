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
CURRENT_ROLE_PATTERN = re.compile(r"\b(present|current|now)\b", re.IGNORECASE)
PRESENT_TENSE_OVERRIDES = {
    "Achieved": "Achieve",
    "Analyzed": "Analyze",
    "Automated": "Automate",
    "Built": "Build",
    "Collaborated": "Collaborate",
    "Coordinated": "Coordinate",
    "Created": "Create",
    "Delivered": "Deliver",
    "Designed": "Design",
    "Developed": "Develop",
    "Directed": "Direct",
    "Drove": "Drive",
    "Established": "Establish",
    "Executed": "Execute",
    "Expanded": "Expand",
    "Facilitated": "Facilitate",
    "Generated": "Generate",
    "Improved": "Improve",
    "Implemented": "Implement",
    "Increased": "Increase",
    "Initiated": "Initiate",
    "Launched": "Launch",
    "Led": "Lead",
    "Maintained": "Maintain",
    "Managed": "Manage",
    "Mentored": "Mentor",
    "Optimized": "Optimize",
    "Owned": "Own",
    "Presented": "Present",
    "Produced": "Produce",
    "Reduced": "Reduce",
    "Resolved": "Resolve",
    "Scaled": "Scale",
    "Secured": "Secure",
    "Spearheaded": "Spearhead",
    "Streamlined": "Streamline",
    "Strengthened": "Strengthen",
    "Supported": "Support",
}


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


def _extract_display_name(source_cv_text: str | None, fallback_full_name: str | None) -> str:
    for line in str(source_cv_text or "").splitlines():
        candidate = re.sub(r"\s+", " ", line).strip()
        if not candidate or len(candidate) > 80:
            continue
        if re.search(r"[@|+/]|https?://|www\.", candidate, re.IGNORECASE):
            continue
        if sum(ch.isalpha() for ch in candidate) < 3:
            continue
        return candidate
    return str(fallback_full_name or "").strip()


def _strip_terminal_period(text: str) -> str:
    return re.sub(r"\.(?=$)", "", text.strip())


def _humanize_bullet(text: str) -> str:
    cleaned = text.replace("—", ", ").replace("–", ", ")
    cleaned = re.sub(r"\s*-\s*", ", ", cleaned)
    cleaned = re.sub(r"\s+,", ",", cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned).strip(" ,")
    return _strip_terminal_period(cleaned)


def _is_current_period(period: str | None) -> bool:
    return bool(CURRENT_ROLE_PATTERN.search(str(period or "")))


def _to_present_tense(text: str) -> str:
    parts = text.split(" ", 1)
    if not parts:
        return text
    replacement = PRESENT_TENSE_OVERRIDES.get(parts[0])
    if not replacement:
        return text
    return replacement if len(parts) == 1 else f"{replacement} {parts[1]}"


def _normalize_bullet(bullet: str, *, current_role: bool = False) -> str:
    cleaned = re.sub(r"^[\-•\s]+", "", str(bullet or "")).strip()
    if not cleaned:
        return ""
    cleaned = _humanize_bullet(cleaned)
    if current_role:
        cleaned = _to_present_tense(cleaned)
    if cleaned:
        cleaned = cleaned[0].upper() + cleaned[1:]
    return cleaned


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
        current_role = _is_current_period(item.get("period"))
        bullets = [_normalize_bullet(b, current_role=current_role) for b in item.get("bullets", [])]
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


def _normalize_education(items: list[dict] | None) -> list[dict]:
    normalized = []
    for item in items or []:
        bullet_sources = list(item.get("bullets") or [])
        details = item.get("details")
        coursework = item.get("coursework")
        if isinstance(details, list):
            bullet_sources.extend(details)
        elif details:
            bullet_sources.append(str(details))
        if isinstance(coursework, list):
            bullet_sources.extend(f"Relevant coursework: {entry}" for entry in coursework)
        elif coursework:
            bullet_sources.append(f"Relevant coursework: {coursework}")
        bullets: list[str] = []
        for entry in bullet_sources:
            cleaned = _normalize_bullet(entry)
            if cleaned:
                bullets.append(cleaned)
        normalized.append(
            {
                "institution": item.get("institution", ""),
                "degree": item.get("degree", ""),
                "gpa": item.get("gpa", ""),
                "year": item.get("year", ""),
                "bullets": bullets,
            }
        )
    return normalized


def _normalize_additional_info(info: dict | None) -> dict[str, list[str] | str]:
    rows: dict[str, list[str] | str] = {}
    for label, value in (info or {}).items():
        if not value:
            continue
        if isinstance(value, list):
            cleaned = [_strip_terminal_period(str(v).strip()) for v in value if str(v).strip()]
            if cleaned:
                rows[str(label)] = cleaned
        else:
            cleaned = _strip_terminal_period(str(value).strip())
            if cleaned:
                rows[str(label)] = cleaned
    return rows


def _separate_project_like_experience(experience: list[dict], extra_miles: list[str]) -> list[dict]:
    kept = []
    for item in experience:
        title = str(item.get("title") or "")
        if re.search(r"bangkit by|capstone|project machine learning lead", title, re.IGNORECASE):
            company = str(item.get("company") or "").strip()
            period = str(item.get("period") or "").strip()
            bullets = [str(b).strip() for b in item.get("bullets") or [] if str(b).strip()]
            summary = " | ".join(part for part in [title, company, period] if part)
            if bullets:
                summary = f"{summary}: {'; '.join(bullets)}" if summary else "; ".join(bullets)
            cleaned = _strip_terminal_period(summary)
            if cleaned and cleaned not in extra_miles:
                extra_miles.append(cleaned)
            continue
        kept.append(item)
    return kept


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
    source_cv_text: str = "",
) -> dict:
    normalized = dict(tailored_data or {})

    display_name = str(normalized.get("display_name") or "").strip() or _extract_display_name(
        source_cv_text,
        getattr(user, "full_name", ""),
    )
    if display_name:
        normalized["display_name"] = display_name

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
    normalized["education"] = _normalize_education(normalized.get("education"))
    normalized["additional_info"] = _normalize_additional_info(normalized.get("additional_info") or {})

    extra_miles = []
    for key in ("awards", "projects", "certifications", "extra_miles"):
        for item in normalized.get(key, []) or []:
            text = _strip_terminal_period(str(item).strip())
            if text and text not in extra_miles:
                extra_miles.append(text)
    normalized["experience"] = _separate_project_like_experience(normalized["experience"], extra_miles)
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
        source_cv_text=cv.raw_text,
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
