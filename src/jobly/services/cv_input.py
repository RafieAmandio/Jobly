import re
from html import unescape

import httpx
from bs4 import BeautifulSoup

LINKEDIN_PROFILE_RE = re.compile(
    r"(?P<url>(?:https?://)?(?:www\.)?linkedin\.com/in/[^\s?#]+)", re.IGNORECASE
)


def _extract_linkedin_url(text: str) -> str | None:
    match = LINKEDIN_PROFILE_RE.search(text.strip())
    if not match:
        return None
    url = match.group("url")
    if not url.startswith(("http://", "https://")):
        url = f"https://{url}"
    return url


async def _fetch_linkedin_profile_summary(url: str) -> dict[str, str] | None:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
        )
    }
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    title = (
        soup.find("meta", property="og:title")
        or soup.find("meta", attrs={"name": "title"})
    )
    description = (
        soup.find("meta", property="og:description")
        or soup.find("meta", attrs={"name": "description"})
    )

    title_text = title.get("content", "").strip() if title else ""
    description_text = description.get("content", "").strip() if description else ""
    if not title_text and soup.title and soup.title.string:
        title_text = soup.title.string.strip()

    if not title_text and not description_text:
        return None
    return {
        "title": unescape(title_text),
        "description": unescape(description_text),
    }


async def prepare_cv_text(text: str) -> str:
    text = text.strip()
    linkedin_url = _extract_linkedin_url(text)
    if not linkedin_url:
        return text

    profile = await _fetch_linkedin_profile_summary(linkedin_url)
    lines = [
        "LinkedIn profile source",
        f"LinkedIn URL: {linkedin_url}",
    ]
    if profile:
        if profile.get("title"):
            lines.append(f"Profile title: {profile['title']}")
        if profile.get("description"):
            lines.append(f"Profile summary: {profile['description']}")
    else:
        lines.append(
            "Use the LinkedIn profile URL above as the candidate's source profile when creating the CV."
        )

    if text != linkedin_url:
        lines.append("")
        lines.append("Additional user-provided text:")
        lines.append(text)

    return "\n".join(lines)
