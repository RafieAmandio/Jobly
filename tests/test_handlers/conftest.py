import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from jobly.models.cv import CV
from jobly.models.job import Job
from jobly.models.user import User
from jobly.services.user import create_user
from tests.factories import MemoryFSMContext, MockBot


@pytest.fixture
def bot():
    return MockBot()


@pytest.fixture
def state():
    return MemoryFSMContext()


@pytest.fixture
async def test_user(seeded_session):
    user = await create_user(
        seeded_session,
        telegram_id=123456789,
        full_name="Test User",
        email="test@example.com",
        language="en",
        telegram_username="testuser",
    )
    await seeded_session.flush()
    result = await seeded_session.execute(
        select(User).where(User.id == user.id).options(selectinload(User.preferences))
    )
    return result.scalar_one()


@pytest.fixture
async def test_job(seeded_session):
    job = Job(
        external_id="test-job-001",
        source="linkedin",
        title="Software Engineer",
        company="Tokopedia",
        description="We are looking for a Software Engineer with 3+ years of Python experience. "
        "Skills: Python, Django, PostgreSQL, Docker, AWS. "
        "Responsibilities: Build scalable APIs, mentor junior engineers.",
        location="Jakarta Selatan",
        work_arrangement="hybrid",
        salary_min=15_000_000,
        salary_max=25_000_000,
        salary_text="Rp 15-25 juta/bulan",
        url="https://linkedin.com/jobs/test-001",
        fingerprint="test-fp-001",
        is_active=True,
    )
    seeded_session.add(job)
    await seeded_session.flush()
    return job


@pytest.fixture
async def test_cv(seeded_session, test_user):
    cv = CV(
        user_id=test_user.id,
        raw_text=(
            "John Doe\nSoftware Engineer\n\n"
            "Experience:\n- Built REST APIs at Company A (2020-2023)\n"
            "- Led team of 5 engineers at Company B (2023-present)\n\n"
            "Skills: Python, Go, PostgreSQL, Docker, Kubernetes\n\n"
            "Education: BS Computer Science, UI (2020)"
        ),
        is_current=True,
    )
    seeded_session.add(cv)
    await seeded_session.flush()
    return cv
