import uuid
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest


@pytest.fixture
def mock_user():
    return SimpleNamespace(
        id=uuid.uuid4(),
        telegram_id=123456789,
        telegram_username="testuser",
        full_name="Test User",
        email="test@example.com",
        phone=None,
        language="id",
        credit_balance=5,
        referral_code="TESTCODE",
        referred_by=None,
        onboarding_completed=True,
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        preferences=None,
    )


@pytest.fixture
def mock_job():
    return SimpleNamespace(
        id=uuid.uuid4(),
        external_id="ext-123",
        source="linkedin",
        title="Software Engineer",
        company="Tokopedia",
        description="Build scalable systems with Python and Go",
        location="Jakarta Selatan",
        work_arrangement="hybrid",
        salary_min=15_000_000,
        salary_max=25_000_000,
        salary_text="Rp 15-25 juta/bulan",
        experience_level="mid",
        url="https://linkedin.com/jobs/123",
        posted_at=datetime.utcnow(),
        scraped_at=datetime.utcnow(),
        is_active=True,
        fingerprint="abc123",
        categories=[],
    )


@pytest.fixture
def mock_cv():
    return SimpleNamespace(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        raw_text=(
            "John Doe\nSoftware Engineer\n\n"
            "Experience:\n- Built REST APIs at Company A (2020-2023)\n"
            "- Led team of 5 engineers at Company B (2023-present)\n\n"
            "Skills: Python, Go, PostgreSQL, Docker, Kubernetes\n\n"
            "Education: BS Computer Science, UI (2020)"
        ),
        parsed_data=None,
        is_current=True,
    )


@pytest.fixture
def mock_session():
    session = AsyncMock()
    session.flush = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    return session
