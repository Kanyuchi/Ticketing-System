import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.ticket_type import TicketType
from app.models.waitlist import WaitlistEntry


async def join_waitlist(
    db: AsyncSession, ticket_type_id: uuid.UUID, email: str, name: str
) -> WaitlistEntry:
    """Add someone to the waitlist for a sold-out ticket type."""
    # Verify ticket type exists
    result = await db.execute(select(TicketType).where(TicketType.id == ticket_type_id))
    tt = result.scalar_one_or_none()
    if not tt:
        raise ValueError("Ticket type not found")

    # Check if sold out (only allow waitlist for sold-out types)
    if tt.quantity_total is None or tt.quantity_sold < tt.quantity_total:
        raise ValueError("Ticket type is not sold out — purchase directly instead")

    # Check not already on waitlist
    result = await db.execute(
        select(WaitlistEntry).where(
            WaitlistEntry.ticket_type_id == ticket_type_id,
            WaitlistEntry.email == email,
        )
    )
    if result.scalar_one_or_none():
        raise ValueError("Already on the waitlist for this ticket type")

    # Get next position
    result = await db.execute(
        select(func.max(WaitlistEntry.position)).where(
            WaitlistEntry.ticket_type_id == ticket_type_id
        )
    )
    max_pos = result.scalar() or 0

    entry = WaitlistEntry(
        ticket_type_id=ticket_type_id,
        email=email,
        name=name,
        position=max_pos + 1,
    )
    db.add(entry)
    await db.flush()
    await db.refresh(entry)
    return entry


async def leave_waitlist(db: AsyncSession, entry_id: uuid.UUID) -> bool:
    result = await db.execute(select(WaitlistEntry).where(WaitlistEntry.id == entry_id))
    entry = result.scalar_one_or_none()
    if not entry:
        return False
    await db.delete(entry)
    await db.flush()
    return True


async def list_waitlist(
    db: AsyncSession, ticket_type_id: uuid.UUID | None = None
) -> list[dict]:
    """List waitlist entries, optionally filtered by ticket type."""
    query = (
        select(WaitlistEntry)
        .options(selectinload(WaitlistEntry.ticket_type))
        .order_by(WaitlistEntry.position)
    )
    if ticket_type_id:
        query = query.where(WaitlistEntry.ticket_type_id == ticket_type_id)

    result = await db.execute(query)
    entries = result.scalars().all()
    return [
        {
            "id": e.id,
            "ticket_type_id": e.ticket_type_id,
            "ticket_type_name": e.ticket_type.name if e.ticket_type else "Unknown",
            "email": e.email,
            "name": e.name,
            "position": e.position,
            "notified": e.notified,
            "created_at": e.created_at,
        }
        for e in entries
    ]


async def notify_next_in_line(
    db: AsyncSession, ticket_type_id: uuid.UUID, count: int = 1
) -> list[WaitlistEntry]:
    """Mark the next N people as notified when spots open up."""
    result = await db.execute(
        select(WaitlistEntry)
        .where(
            WaitlistEntry.ticket_type_id == ticket_type_id,
            WaitlistEntry.notified == False,
        )
        .order_by(WaitlistEntry.position)
        .limit(count)
    )
    entries = result.scalars().all()
    from datetime import datetime, timezone
    for entry in entries:
        entry.notified = True
        entry.notified_at = datetime.now(timezone.utc)
    await db.flush()
    return list(entries)
