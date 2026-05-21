import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from jobly.models.credit import Payment
from jobly.models.user import User
from jobly.services.user import create_user


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
async def test_payment(seeded_session, test_user):
    payment = Payment(
        user_id=test_user.id,
        xendit_external_id="test-ext-123",
        package_name="popular",
        credits=15,
        amount_idr=60_000,
        status="pending",
    )
    seeded_session.add(payment)
    await seeded_session.flush()
    return payment
