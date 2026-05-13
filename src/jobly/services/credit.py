from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from jobly.models.credit import CreditTransaction
from jobly.models.user import User


async def get_balance(session: AsyncSession, user: User) -> int:
    return user.credit_balance


async def deduct_credit(
    session: AsyncSession,
    user: User,
    amount: int,
    type: str,
    reference_id: str | None = None,
    description: str | None = None,
) -> bool:
    if user.credit_balance < amount:
        return False

    user.credit_balance -= amount
    tx = CreditTransaction(
        user_id=user.id,
        amount=-amount,
        balance_after=user.credit_balance,
        type=type,
        reference_id=reference_id,
        description=description,
    )
    session.add(tx)
    await session.flush()
    return True


async def add_credit(
    session: AsyncSession,
    user: User,
    amount: int,
    type: str,
    reference_id: str | None = None,
    description: str | None = None,
) -> int:
    user.credit_balance += amount
    tx = CreditTransaction(
        user_id=user.id,
        amount=amount,
        balance_after=user.credit_balance,
        type=type,
        reference_id=reference_id,
        description=description,
    )
    session.add(tx)
    await session.flush()
    return user.credit_balance


async def get_transaction_history(
    session: AsyncSession, user: User, limit: int = 20
) -> list[CreditTransaction]:
    result = await session.execute(
        select(CreditTransaction)
        .where(CreditTransaction.user_id == user.id)
        .order_by(CreditTransaction.created_at.desc())
        .limit(limit)
    )
    return list(result.scalars().all())
