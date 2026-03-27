"""Referral rewards automation.

When a referrer hits a threshold (e.g., 5 referred orders), they get
auto-upgraded. The reward rules are configurable per-deployment.
"""
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.referral import Referral
from app.models.voucher import Voucher
from app.services.voucher_service import bulk_create_vouchers

# Default reward tiers — can be overridden via config
REWARD_TIERS = [
    {"min_orders": 3, "reward": "voucher", "ticket_category": "general", "label": "Bronze Ambassador"},
    {"min_orders": 5, "reward": "voucher", "ticket_category": "vip", "label": "Silver Ambassador"},
    {"min_orders": 10, "reward": "voucher", "ticket_category": "vip_black", "label": "Gold Ambassador"},
]


async def check_and_apply_rewards(
    db: AsyncSession, referral_code: str
) -> dict | None:
    """Check if a referrer has earned a new reward tier.

    Returns reward info if a new tier was reached, None otherwise.
    """
    result = await db.execute(select(Referral).where(Referral.code == referral_code))
    referral = result.scalar_one_or_none()
    if not referral:
        return None

    # Find the highest tier they qualify for
    earned_tier = None
    for tier in sorted(REWARD_TIERS, key=lambda t: t["min_orders"], reverse=True):
        if referral.orders_count >= tier["min_orders"]:
            earned_tier = tier
            break

    if not earned_tier:
        return None

    # Check if they already have a voucher for this tier (avoid duplicates)
    prefix = f"REWARD-{earned_tier['label'].upper().replace(' ', '-')}"
    result = await db.execute(
        select(Voucher).where(
            Voucher.code.startswith(prefix),
            Voucher.used_by_email == None,  # noqa: E711 — SQLAlchemy needs `== None`
        )
    )
    # Look for existing reward voucher for this referrer's email
    result = await db.execute(
        select(Voucher).where(
            Voucher.code.like(f"{prefix}%"),
        )
    )
    existing = result.scalars().all()
    # If voucher already generated for this tier, skip
    for v in existing:
        if v.code.endswith(referral.code):
            return {"tier": earned_tier["label"], "already_awarded": True}

    # Find matching ticket type
    from app.models.ticket_type import TicketType, TicketCategory
    cat = TicketCategory(earned_tier["ticket_category"])
    result = await db.execute(
        select(TicketType).where(TicketType.category == cat, TicketType.is_active == True)
    )
    ticket_type = result.scalars().first()
    if not ticket_type:
        return None  # ticket type not found, can't award

    # Generate a unique reward voucher
    code = f"{prefix}-{referral.code}"
    voucher = Voucher(
        code=code,
        ticket_type_id=ticket_type.id,
        is_used=False,
    )
    db.add(voucher)
    await db.flush()

    return {
        "tier": earned_tier["label"],
        "voucher_code": code,
        "ticket_type": ticket_type.name,
        "already_awarded": False,
    }


async def get_referral_reward_status(db: AsyncSession, referral_code: str) -> dict:
    """Get current reward status for a referral code."""
    result = await db.execute(select(Referral).where(Referral.code == referral_code))
    referral = result.scalar_one_or_none()
    if not referral:
        raise ValueError("Referral not found")

    current_tier = None
    next_tier = None
    orders_to_next = None

    for tier in sorted(REWARD_TIERS, key=lambda t: t["min_orders"]):
        if referral.orders_count >= tier["min_orders"]:
            current_tier = tier
        elif next_tier is None:
            next_tier = tier
            orders_to_next = tier["min_orders"] - referral.orders_count

    return {
        "referral_code": referral.code,
        "orders_count": referral.orders_count,
        "current_tier": current_tier["label"] if current_tier else None,
        "next_tier": next_tier["label"] if next_tier else None,
        "orders_to_next_tier": orders_to_next,
    }
