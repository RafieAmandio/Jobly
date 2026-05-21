import pytest

from jobly.services.ai import classify_job, generate_cover_letter_content, tailor_cv_content


@pytest.mark.integration
@pytest.mark.asyncio
async def test_tailor_cv_returns_valid_json():
    result = await tailor_cv_content(
        cv_text=(
            "Jane Doe\nSoftware Engineer\n\n"
            "Experience:\n- Built REST APIs at Gojek (2021-2024)\n"
            "Skills: Python, FastAPI, PostgreSQL\n"
            "Education: BS Computer Science, ITB (2021)"
        ),
        job_description=(
            "Looking for a Backend Engineer with 3+ years Python. "
            "Must know Django, PostgreSQL, Docker. "
            "Will build microservices for e-commerce platform."
        ),
        job_title="Backend Engineer",
        company="Tokopedia",
        lang="en",
    )
    assert result is not None
    assert "summary" in result or "experience" in result


@pytest.mark.integration
@pytest.mark.asyncio
async def test_cover_letter_returns_text():
    result = await generate_cover_letter_content(
        cv_text="Jane Doe, 3 years Python experience at Gojek.",
        job_description="Backend Engineer at Tokopedia. Python, Django, PostgreSQL.",
        job_title="Backend Engineer",
        company="Tokopedia",
        lang="en",
    )
    assert result is not None
    assert len(result) > 50


@pytest.mark.integration
@pytest.mark.asyncio
async def test_classify_job_returns_categories():
    result = await classify_job(
        title="Senior Python Developer",
        description="Build backend services using Python, Django, PostgreSQL. "
        "Lead a team of 3 engineers. 5+ years experience required.",
    )
    assert len(result) >= 1
    assert "slug" in result[0]
    assert "confidence" in result[0]
