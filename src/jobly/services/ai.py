import json
import logging
import re

from openai import AsyncOpenAI

from jobly.config import settings

logger = logging.getLogger(__name__)


def _extract_json(text: str) -> str:
    """Strip markdown code fences from AI response before JSON parsing."""
    m = re.search(r"```(?:json)?\s*\n?(.*?)```", text, re.DOTALL)
    return m.group(1).strip() if m else text.strip()

_client: AsyncOpenAI | None = None


def get_ai_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.moonshot.api_key,
            base_url=settings.moonshot.base_url,
        )
    return _client


async def tailor_cv_content(
    cv_text: str, job_description: str, job_title: str, company: str, lang: str = "id"
) -> dict | None:
    client = get_ai_client()
    lang_name = "Bahasa Indonesia" if lang == "id" else "English"

    try:
        response = await client.chat.completions.create(
            model=settings.moonshot.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert CV writer specializing in the Indonesian job market. "
                        "You tailor CVs to match specific job descriptions while keeping the content "
                        "truthful to the candidate's actual experience. Follow these CV formatting rules: "
                        "personal info should use name, broad-area location only (not full detailed address), "
                        "phone should be suitable for +62 formatting, and email plus portfolio/link should be "
                        "kept usable as hyperlinks; work and leadership descriptions must be bullet points only, "
                        "maximum 3 bullets each, with quantified impact whenever possible; education should "
                        "highlight achievements/activities briefly; extra achievements can go in an extra-miles "
                        "style section; skills should be grouped into technical, soft, and tools; the final CV "
                        "should stay concise and relevant, targeting a maximum of 2 pages in a clean ATS-friendly format.\n\n"
                        "Instructions:\n"
                        "1. Analyze the job description for key requirements, skills, and keywords\n"
                        "2. Rewrite the CV sections to emphasize only the most relevant experience for this role\n"
                        "3. Adjust the professional summary to align with the role and keep it concise\n"
                        "4. Naturally incorporate role-relevant keywords from the job description into summary, experience, leadership, and skills without keyword stuffing\n"
                        "5. Rephrase bullet points using strong active verbs and quantified achievements\n"
                        "6. Use only metrics, scope, and data that are already supported by the source CV; never invent numbers or impact\n"
                        "7. Keep all factual information (dates, companies, degrees) unchanged and keep the tone genuine\n"
                        "8. Extract the candidate's contact details (broad-area location, email, phone, "
                        "LinkedIn URL or portfolio link) from the CV into the 'contact' object. Omit any field "
                        "not present in the CV; never invent contact details.\n"
                        "9. Include a 'leadership' section when the CV contains organizations, committees, "
                        "volunteering, or campus leadership relevant to the role.\n"
                        "10. If the CV lists certifications, awards/achievements, or notable "
                        "projects, include the most relevant ones as short one-line strings for an extra-miles "
                        "style section. Omit a section entirely if the CV has none.\n"
                        f"11. Output in {lang_name}\n\n"
                        "Output valid JSON with this structure:\n"
                        '{"contact": {"location": "...", "email": "...", "phone": "...", "portfolio": "...", "linkedin": "..."}, '
                        '"summary": "...", "experience": [{"company": "...", "title": "...", '
                        '"period": "...", "bullets": ["..."]}], '
                        '"leadership": [{"organization": "...", "title": "...", "period": "...", "brief": "...", "bullets": ["..."]}], '
                        '"education": [{"institution": "...", "degree": "...", "year": "...", "details": "..."}], '
                        '"extra_miles": ["..."], '
                        '"skills": {"technical": ["..."], "soft": ["..."], "tools": ["..."]}}'
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Job Title: {job_title}\nCompany: {company}\n\n"
                        f"Job Description:\n{job_description}\n\n"
                        f"Current CV:\n{cv_text}"
                    ),
                },
            ],
            temperature=1,
        )
        content = response.choices[0].message.content
        return json.loads(_extract_json(content))
    except Exception:
        logger.exception("Failed to tailor CV via AI")
        return None


async def generate_cover_letter_content(
    cv_text: str,
    job_description: str,
    job_title: str,
    company: str,
    lang: str = "id",
    candidate_level: str | None = None,
) -> str | None:
    client = get_ai_client()
    lang_name = "Bahasa Indonesia" if lang == "id" else "English"
    level_hint = candidate_level or "unknown"

    try:
        response = await client.chat.completions.create(
            model=settings.moonshot.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert cover letter writer for the Indonesian job market. "
                        "Generate a professional, personalized cover letter that follows this exact guideline.\n\n"
                        "Instructions:\n"
                        "1. Adapt the seniority and examples to the candidate level/rank provided.\n"
                        '2. Include a formal recipient line (use "Yth. HRD {company}" in Indonesian or "Dear Hiring Manager at {company}" in English when no name is available).\n'
                        "3. Include a clear formal subject line that states the application intent.\n"
                        "4. First paragraph: introduce the candidate and highlight the most recent, most impactful milestone.\n"
                        "5. Middle paragraph: show passion/interest and connect it to past leadership experience when available.\n"
                        "6. Middle paragraph: show the ultimate value added by proving the candidate has already operated in a professional field (internship, program, business, freelance, etc.).\n"
                        "7. Explicitly bridge the candidate's background to the value they can offer this company and role.\n"
                        "8. End with a warm professional closing.\n"
                        "9. Keep the writing neat, structured, simple, and laser-focused.\n"
                        "10. Keep to roughly 250-350 words and 4-6 short paragraphs after the subject/recipient lines.\n"
                        f"11. Language: {lang_name}\n"
                        "12. Output plain text only. Do not use markdown, bullet points, placeholders, or JSON.\n\n"
                        "Output the cover letter text only, no JSON wrapper."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Job Title: {job_title}\nCompany: {company}\nCandidate Level: {level_hint}\n\n"
                        f"Job Description:\n{job_description}\n\n"
                        f"Candidate CV:\n{cv_text}"
                    ),
                },
            ],
            temperature=1,
        )
        return response.choices[0].message.content
    except Exception:
        logger.exception("Failed to generate cover letter via AI")
        return None


async def classify_job(title: str, description: str) -> list[dict]:
    client = get_ai_client()

    try:
        response = await client.chat.completions.create(
            model=settings.moonshot.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Classify this job posting into categories. Return a JSON array of objects "
                        'with "slug" and "confidence" fields.\n\n'
                        "Available categories: technology, data_science_ai, software_engineering, "
                        "finance_accounting, banking, fintech, marketing, digital_marketing, sales, "
                        "human_resources, customer_service, administration, engineering, manufacturing, "
                        "quality_assurance, logistics, healthcare, pharmaceutical, education, research, "
                        "legal, creative_design, media, hospitality, food_beverage, retail, ecommerce, "
                        "real_estate, construction, telecommunications, automotive, mining, agriculture, "
                        "environment, insurance, consulting, government, social_ngo, fmcg, aviation\n\n"
                        "Return 1-3 most relevant categories. Confidence between 0 and 1."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Job Title: {title}\n\nDescription:\n{description[:2000]}",
                },
            ],
            temperature=1,
        )
        content = response.choices[0].message.content
        data = json.loads(_extract_json(content))
        if isinstance(data, dict) and "categories" in data:
            return data["categories"]
        if isinstance(data, list):
            return data
        return []
    except Exception:
        logger.exception("Failed to classify job")
        return []
