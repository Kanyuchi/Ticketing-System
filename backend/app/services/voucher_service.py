import random
import string
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.voucher import Voucher


def _generate_code(prefix: str) -> str:
    suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{suffix}"


async def bulk_create_vouchers(
    db: AsyncSession, ticket_type_id: uuid.UUID, prefix: str, count: int
) -> list[Voucher]:
    vouchers = []
    existing_codes: set[str] = set()

    # Fetch existing codes with this prefix to avoid collisions
    result = await db.execute(select(Voucher.code).where(Voucher.code.like(f"{prefix}-%")))
    existing_codes = {row[0] for row in result.all()}

    for _ in range(count):
        code = _generate_code(prefix)
        while code in existing_codes:
            code = _generate_code(prefix)
        existing_codes.add(code)

        voucher = Voucher(code=code, ticket_type_id=ticket_type_id)
        db.add(voucher)
        vouchers.append(voucher)

    await db.flush()
    return vouchers


async def get_voucher_by_code(db: AsyncSession, code: str) -> Voucher | None:
    result = await db.execute(select(Voucher).where(Voucher.code == code))
    return result.scalar_one_or_none()


async def list_vouchers(
    db: AsyncSession, ticket_type_id: uuid.UUID | None = None
) -> list[Voucher]:
    query = select(Voucher).order_by(Voucher.created_at.desc())
    if ticket_type_id:
        query = query.where(Voucher.ticket_type_id == ticket_type_id)
    result = await db.execute(query)
    return list(result.scalars().all())
