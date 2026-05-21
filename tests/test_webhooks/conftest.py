import pytest

from jobly.models.credit import Payment


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
