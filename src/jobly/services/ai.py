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
                        "truthful to the candidate's actual experience.\n\n"
                        "Instructions:\n"
                        "1. Analyze the job description for key requirements, skills, and keywords\n"
                        "2. Rewrite the CV sections to emphasize relevant experience\n"
                        "3. Adjust the professional summary to align with the role\n"
                        "4. Reorder skills to prioritize those mentioned in the JD\n"
                        "5. Rephrase bullet points using action verbs and quantified achievements\n"
                        "6. Keep all factual information (dates, companies, degrees) unchanged\n"
                        "7. Extract the candidate's contact details (location, email, phone, "
                        "LinkedIn URL) from the CV into the 'contact' object. Omit any field "
                        "not present in the CV; never invent contact details.\n"
                        "8. If the CV lists certifications, awards/achievements, or notable "
                        "projects, include the most relevant ones (each as a short one-line "
                        "string). Omit a section entirely if the CV has none.\n"
                        f"9. Output in {lang_name}\n\n"
                        "Output valid JSON with this structure:\n"
                        '{"contact": {"location": "...", "email": "...", "phone": "...", "linkedin": "..."}, '
                        '"summary": "...", "experience": [{"company": "...", "title": "...", '
                        '"period": "...", "bullets": ["..."]}], '
                        '"education": [{"institution": "...", "degree": "...", "year": "..."}], '
                        '"certifications": ["..."], "awards": ["..."], "projects": ["..."], '
                        '"skills": ["..."]}'
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
    cv_text: str, job_description: str, job_title: str, company: str, lang: str = "id"
) -> str | None:
    client = get_ai_client()
    lang_name = "Bahasa Indonesia" if lang == "id" else "English"

    try:
        response = await client.chat.completions.create(
            model=settings.moonshot.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert cover letter writer for the Indonesian job market. "
                        "Generate a professional, personalized cover letter.\n\n"
                        "Instructions:\n"
                        '1. Address the hiring manager (use "Yth. HRD {company}" if no name)\n'
                        "2. Opening: hook connecting candidate's passion to the role\n"
                        "3. Body: 2-3 paragraphs mapping achievements to JD requirements\n"
                        "4. Closing: call to action, availability, gratitude\n"
                        "5. Keep to ~300-400 words\n"
                        "6. Tone: professional but warm\n"
                        f"7. Language: {lang_name}\n\n"
                        "Output the cover letter text only, no JSON wrapper."
                    ),
                },
                {
                    "role": "user",
                    "content": (
                        f"Job Title: {job_title}\nCompany: {company}\n\n"
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
