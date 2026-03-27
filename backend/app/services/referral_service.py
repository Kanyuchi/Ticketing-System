import random
import string
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.referral import Referral, ReferralAttribution


def _generate_referral_code() -> str:
    chars = string.ascii_uppercase + string.digits
    return "REF-" + "".join(random.choices(chars, k=8))


async def create_referral(
    db: AsyncSession, owner_name: str, owner_email: str, code: str | None = None
) -> Referral:
    if code:
        # Check uniqueness
        result = await db.execute(select(Referral).where(Referral.code == code))
        if result.scalar_one_or_none():
            raise ValueError("Referral code already exists")
    else:
        code = _generate_referral_code()
        # Ensure uniqueness
        while True:
            result = await db.execute(select(Referral).where(Referral.code == code))
            if not result.scalar_one_or_none():
                break
            code = _generate_referral_code()

    referral = Referral(code=code, owner_name=owner_name, owner_email=owner_email)
    db.add(referral)
    await db.flush()
    await db.refresh(referral)
    return referral


async def track_click(db: AsyncSession, code: str) -> Referral | None:
    result = await db.execute(select(Referral).where(Referral.code == code))
    referral = result.scalar_one_or_none()
    if referral:
        referral.clicks += 1
        await db.flush()
    return referral


async def attribute_order(db: AsyncSession, referral_code: str, order_id: uuid.UUID) -> bool:
    """Attribute an order to a referral. Returns True if successful."""
    # Get referral
    result = await db.execute(select(Referral).where(Referral.code == referral_code))
    referral = result.scalar_one_or_none()
    if not referral:
        return False

    # Check not already attributed
    result = await db.execute(
        select(ReferralAttribution).where(ReferralAttribution.order_id == order_id)
    )
    if result.scalar_one_or_none():
        return False  # already attributed

    # Get order total
    result = await db.execute(select(Order).where(Order.id == order_id))
    order = result.scalar_one_or_none()
    if not order:
        return False

    attribution = ReferralAttribution(referral_id=referral.id, order_id=order_id)
    db.add(attribution)

    referral.orders_count += 1
    referral.revenue_eur += order.total_eur

    await db.flush()
    return True


async def get_referral_by_code(db: AsyncSession, code: str) -> Referral | None:
    result = await db.execute(select(Referral).where(Referral.code == code))
    return result.scalar_one_or_none()


async def list_referrals(db: AsyncSession) -> list[Referral]:
    result = await db.execute(select(Referral).order_by(Referral.revenue_eur.desc()))
    return list(result.scalars().all())


async def get_referral_stats(db: AsyncSession, referral_id: uuid.UUID) -> dict:
    result = await db.execute(select(Referral).where(Referral.id == referral_id))
    ref = result.scalar_one_or_none()
    if not ref:
        raise ValueError("Referral not found")
    return {
        "id": ref.id,
        "code": ref.code,
        "owner_name": ref.owner_name,
        "owner_email": ref.owner_email,
        "clicks": ref.clicks,
        "orders_count": ref.orders_count,
        "revenue_eur": ref.revenue_eur,
        "conversion_rate": ref.orders_count / ref.clicks if ref.clicks > 0 else 0.0,
    }
