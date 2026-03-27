"""Seed the database with initial ticket types, admin user, and demo referral."""
import asyncio

from sqlalchemy import select

from app.core.database import Base, async_session, engine
from app.core.security import hash_password
from app.models.admin_user import AdminUser
from app.models.referral import Referral
from app.models.ticket_type import TicketCategory, TicketType
# Import all models so create_all picks up every table
from app.models import *  # noqa: F401, F403


TICKET_TYPES = [
    {"name": "VIP Black Pass", "category": TicketCategory.VIP_BLACK, "price_eur": 349900, "quantity_total": 50, "sort_order": 1},
    {"name": "Investor Pass", "category": TicketCategory.INVESTOR, "price_eur": 299900, "quantity_total": 100, "sort_order": 2},
    {"name": "VIP Pass", "category": TicketCategory.VIP, "price_eur": 249900, "quantity_total": 200, "sort_order": 3},
    {"name": "General Pass", "category": TicketCategory.GENERAL, "price_eur": 119900, "quantity_total": 500, "sort_order": 4},
    {
        "name": "Startup Pass",
        "category": TicketCategory.STARTUP,
        "price_eur": 99900,
        "requires_application": True,
        "quantity_total": 100,
        "sort_order": 5,
    },
    {
        "name": "Press Pass",
        "category": TicketCategory.PRESS,
        "price_eur": 0,
        "is_complimentary": True,
        "requires_application": True,
        "quantity_total": 50,
        "sort_order": 6,
    },
    {
        "name": "Speaker Pass",
        "category": TicketCategory.SPEAKER,
        "price_eur": 0,
        "is_complimentary": True,
        "sort_order": 7,
    },
    {
        "name": "Partner Pass",
        "category": TicketCategory.PARTNER,
        "price_eur": 0,
        "is_complimentary": True,
        "sort_order": 8,
    },
]

DEMO_REFERRALS = [
    {"code": "POT-AMBASSADOR", "owner_name": "Demo Ambassador", "owner_email": "ambassador@proofoftalk.io"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        # Seed ticket types
        for tt_data in TICKET_TYPES:
            result = await session.execute(
                select(TicketType).where(TicketType.category == tt_data["category"])
            )
            if not result.scalar_one_or_none():
                session.add(TicketType(**tt_data))
                print(f"  + {tt_data['name']}")

        # Seed admin user
        result = await session.execute(
            select(AdminUser).where(AdminUser.email == "admin@proofoftalk.io")
        )
        if not result.scalar_one_or_none():
            session.add(
                AdminUser(
                    email="admin@proofoftalk.io",
                    hashed_password=hash_password("changeme123"),
                    name="Admin",
                )
            )
            print("  + Admin user (admin@proofoftalk.io)")

        # Seed demo referrals
        for ref_data in DEMO_REFERRALS:
            result = await session.execute(
                select(Referral).where(Referral.code == ref_data["code"])
            )
            if not result.scalar_one_or_none():
                session.add(Referral(**ref_data))
                print(f"  + Referral: {ref_data['code']}")

        await session.commit()
        print("\nSeed complete.")


if __name__ == "__main__":
    asyncio.run(seed())
