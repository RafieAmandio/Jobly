import logging
import uuid

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.config import settings
from jobly.models.credit import Payment
from jobly.models.user import User
from jobly.services.credit import add_credit

logger = logging.getLogger(__name__)

XENDIT_BASE_URL = "https://api.xendit.co"


async def create_xendit_invoice(
    session: AsyncSession,
    user: User,
    package: dict,
) -> str | None:
    external_id = f"jobly-{user.id}-{uuid.uuid4().hex[:8]}"

    payment = Payment(
        user_id=user.id,
        xendit_external_id=external_id,
        package_name=package["name"],
        credits=package["credits"],
        amount_idr=package["price_idr"],
        status="pending",
    )
    session.add(payment)
    await session.flush()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{XENDIT_BASE_URL}/v2/invoices",
                auth=(settings.xendit.secret_key, ""),
                json={
                    "external_id": external_id,
                    "amount": package["price_idr"],
                    "currency": "IDR",
                    "description": f"Jobly {package['label']} — {package['credits']} credits",
                    "customer": {
                        "given_names": user.full_name,
                        "email": user.email,
                    },
                    "success_redirect_url": "https://t.me/JoblyBot",
                    "failure_redirect_url": "https://t.me/JoblyBot",
                },
            )
            response.raise_for_status()
            data = response.json()

        payment.xendit_invoice_id = data.get("id")
        await session.flush()
        return data.get("invoice_url")
    except Exception:
        logger.exception("Failed to create Xendit invoice")
        payment.status = "failed"
        await session.flush()
        return None


async def handle_xendit_webhook(
    session: AsyncSession, payload: dict
) -> bool:
    external_id = payload.get("external_id", "")
    status = payload.get("status", "")

    from sqlalchemy import select

    payment = (
        await session.execute(
            select(Payment).where(Payment.xendit_external_id == external_id)
        )
    ).scalar_one_or_none()

    if not payment:
        logger.warning(f"Payment not found for external_id: {external_id}")
        return False

    payment.status = status.lower()
    payment.payment_method = payload.get("payment_method")
    payment.xendit_callback_data = payload

    if status.upper() == "PAID":
        from datetime import datetime

        payment.paid_at = datetime.utcnow()

        user = await session.get(User, payment.user_id)
        if user:
            await add_credit(
                session,
                user,
                payment.credits,
                "purchase",
                reference_id=external_id,
                description=f"Top-up {payment.package_name}: {payment.credits} credits",
            )

    await session.flush()
    return True
