import pytest
from sqlalchemy import select

from jobly.models.credit import CreditTransaction, Payment
from jobly.models.user import User
from jobly.services.payment import handle_xendit_webhook


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


@pytest.mark.asyncio
async def test_webhook_paid(seeded_session, test_user, test_payment):
    original_balance = test_user.credit_balance

    payload = {
        "external_id": "test-ext-123",
        "status": "PAID",
        "payment_method": "EWALLET",
    }

    result = await handle_xendit_webhook(seeded_session, payload)

    assert result is True
    assert test_payment.status == "paid"
    assert test_payment.paid_at is not None
    assert test_user.credit_balance == original_balance + 15

    tx = (
        await seeded_session.execute(
            select(CreditTransaction).where(
                CreditTransaction.user_id == test_user.id,
                CreditTransaction.type == "purchase",
            )
        )
    ).scalar_one()
    assert tx.amount == 15


@pytest.mark.asyncio
async def test_webhook_invalid_external_id(seeded_session):
    payload = {
        "external_id": "nonexistent-id",
        "status": "PAID",
    }
    result = await handle_xendit_webhook(seeded_session, payload)
    assert result is False


@pytest.mark.asyncio
async def test_webhook_expired(seeded_session, test_user, test_payment):
    original_balance = test_user.credit_balance

    payload = {
        "external_id": "test-ext-123",
        "status": "EXPIRED",
    }

    result = await handle_xendit_webhook(seeded_session, payload)

    assert result is True
    assert test_payment.status == "expired"
    assert test_user.credit_balance == original_balance
