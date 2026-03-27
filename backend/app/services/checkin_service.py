import uuid
from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.checkin import CheckIn
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.ticket_type import TicketType


async def check_in_order(
    db: AsyncSession,
    order_id: uuid.UUID,
    checked_in_by: str | None = None,
    device_id: str | None = None,
    notes: str | None = None,
    checked_in_at: datetime | None = None,
    is_synced: bool = True,
) -> CheckIn:
    """Check in an attendee by order ID. Order must be confirmed."""
    # Verify order exists and is confirmed
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("Order not found")
    if order.status != OrderStatus.CONFIRMED:
        raise ValueError("Order is not confirmed — cannot check in")

    # Check not already checked in
    result = await db.execute(select(CheckIn).where(CheckIn.order_id == order_id))
    if result.scalar_one_or_none():
        raise ValueError("Already checked in")

    checkin = CheckIn(
        order_id=order_id,
        checked_in_by=checked_in_by,
        device_id=device_id,
        notes=notes,
        is_synced=is_synced,
    )
    if checked_in_at:
        checkin.checked_in_at = checked_in_at

    db.add(checkin)
    await db.flush()
    await db.refresh(checkin)
    return checkin


async def batch_sync_checkins(
    db: AsyncSession,
    entries: list[dict],
    checked_in_by: str | None = None,
) -> list[dict]:
    """Sync a batch of offline check-ins. Returns results per entry."""
    results = []
    for entry in entries:
        try:
            await check_in_order(
                db,
                order_id=entry["order_id"],
                checked_in_by=checked_in_by,
                device_id=entry.get("device_id"),
                notes=entry.get("notes"),
                checked_in_at=entry.get("checked_in_at"),
                is_synced=True,  # now synced
            )
            results.append({"order_id": str(entry["order_id"]), "status": "ok"})
        except ValueError as e:
            results.append({"order_id": str(entry["order_id"]), "status": "error", "detail": str(e)})
    return results


async def get_checkin_by_order(db: AsyncSession, order_id: uuid.UUID) -> CheckIn | None:
    result = await db.execute(select(CheckIn).where(CheckIn.order_id == order_id))
    return result.scalar_one_or_none()


async def list_checkins(db: AsyncSession) -> list[dict]:
    """List all check-ins with order + attendee info."""
    result = await db.execute(
        select(CheckIn)
        .join(Order, CheckIn.order_id == Order.id)
        .options(selectinload(CheckIn.order).selectinload(Order.attendee))
        .order_by(CheckIn.checked_in_at.desc())
    )
    checkins = result.scalars().all()
    out = []
    for c in checkins:
        # Get ticket type name from first item
        item_result = await db.execute(
            select(OrderItem)
            .where(OrderItem.order_id == c.order_id)
            .options(selectinload(OrderItem.ticket_type))
        )
        item = item_result.scalars().first()
        ticket_name = item.ticket_type.name if item and item.ticket_type else "Unknown"

        out.append({
            "id": c.id,
            "order_id": c.order_id,
            "order_number": c.order.order_number,
            "attendee_name": c.order.attendee.name,
            "attendee_email": c.order.attendee.email,
            "ticket_type": ticket_name,
            "checked_in_by": c.checked_in_by,
            "device_id": c.device_id,
            "notes": c.notes,
            "checked_in_at": c.checked_in_at,
        })
    return out


async def get_checkin_stats(db: AsyncSession) -> dict:
    """Check-in rate: confirmed orders vs checked-in."""
    confirmed_result = await db.execute(
        select(func.count()).select_from(Order).where(Order.status == OrderStatus.CONFIRMED)
    )
    total_confirmed = confirmed_result.scalar() or 0

    checkin_result = await db.execute(select(func.count()).select_from(CheckIn))
    total_checked_in = checkin_result.scalar() or 0

    return {
        "total_confirmed": total_confirmed,
        "total_checked_in": total_checked_in,
        "check_in_rate": total_checked_in / total_confirmed if total_confirmed > 0 else 0.0,
    }
