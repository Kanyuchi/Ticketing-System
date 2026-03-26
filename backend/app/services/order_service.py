import random
import string
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.attendee import Attendee
from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.order_item import OrderItem
from app.models.ticket_type import TicketType
from app.models.voucher import Voucher
from app.schemas.order import OrderCreate


def _generate_order_number() -> str:
    chars = string.ascii_uppercase + string.digits
    suffix = "".join(random.choices(chars, k=8))
    return f"POT-{suffix}"


async def create_order(db: AsyncSession, data: OrderCreate) -> Order:
    # Get or create attendee
    result = await db.execute(select(Attendee).where(Attendee.email == data.attendee.email))
    attendee = result.scalar_one_or_none()
    if not attendee:
        attendee = Attendee(
            email=data.attendee.email,
            name=data.attendee.name,
            company=data.attendee.company,
            title=data.attendee.title,
        )
        db.add(attendee)
        await db.flush()
    else:
        attendee.name = data.attendee.name
        if data.attendee.company:
            attendee.company = data.attendee.company
        if data.attendee.title:
            attendee.title = data.attendee.title

    # Resolve voucher if provided
    voucher = None
    if data.voucher_code:
        result = await db.execute(
            select(Voucher).where(Voucher.code == data.voucher_code, Voucher.is_used == False)
        )
        voucher = result.scalar_one_or_none()
        if not voucher:
            raise ValueError("Invalid or already-used voucher code")

    # Build order
    order = Order(
        order_number=_generate_order_number(),
        attendee_id=attendee.id,
        voucher_code=data.voucher_code,
    )
    db.add(order)
    await db.flush()

    total = 0
    for item_data in data.items:
        result = await db.execute(select(TicketType).where(TicketType.id == item_data.ticket_type_id))
        ticket_type = result.scalar_one_or_none()
        if not ticket_type:
            raise ValueError(f"Ticket type {item_data.ticket_type_id} not found")
        if not ticket_type.is_active:
            raise ValueError(f"Ticket type {ticket_type.name} is not available")
        if ticket_type.quantity_total and ticket_type.quantity_sold + item_data.quantity > ticket_type.quantity_total:
            raise ValueError(f"Not enough {ticket_type.name} tickets available")

        # If voucher matches this ticket type, price is 0
        unit_price = 0 if (voucher and voucher.ticket_type_id == ticket_type.id) else ticket_type.price_eur
        if ticket_type.is_complimentary:
            unit_price = 0

        item = OrderItem(
            order_id=order.id,
            ticket_type_id=ticket_type.id,
            quantity=item_data.quantity,
            unit_price_eur=unit_price,
        )
        db.add(item)
        total += unit_price * item_data.quantity

        ticket_type.quantity_sold += item_data.quantity

    order.total_eur = total

    if total == 0:
        order.status = OrderStatus.CONFIRMED
        order.payment_status = PaymentStatus.COMPLIMENTARY

    # Mark voucher as used
    if voucher:
        voucher.is_used = True
        voucher.used_by_email = data.attendee.email
        from datetime import datetime, timezone
        voucher.used_at = datetime.now(timezone.utc)

    await db.flush()

    # Reload with relationships
    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    return result.scalar_one()


async def get_order(db: AsyncSession, order_id: uuid.UUID) -> Order | None:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    return result.scalar_one_or_none()


async def get_order_by_number(db: AsyncSession, order_number: str) -> Order | None:
    result = await db.execute(
        select(Order)
        .where(Order.order_number == order_number)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    return result.scalar_one_or_none()
