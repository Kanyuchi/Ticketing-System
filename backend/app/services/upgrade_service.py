import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order, OrderStatus, PaymentStatus
from app.models.order_item import OrderItem
from app.models.ticket_type import TicketType


async def calculate_upgrade(
    db: AsyncSession, order_id: uuid.UUID, new_ticket_type_id: uuid.UUID, discount_code: str | None = None
) -> dict:
    """Calculate the price difference for upgrading a ticket within an order."""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items), selectinload(Order.attendee))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("Order not found")
    if order.status == OrderStatus.CANCELLED:
        raise ValueError("Cannot upgrade a cancelled order")

    if not order.items:
        raise ValueError("Order has no items")

    # Get current ticket type from first item
    current_item = order.items[0]
    result = await db.execute(select(TicketType).where(TicketType.id == current_item.ticket_type_id))
    current_type = result.scalar_one()

    # Get new ticket type
    result = await db.execute(select(TicketType).where(TicketType.id == new_ticket_type_id))
    new_type = result.scalar_one_or_none()
    if not new_type:
        raise ValueError("Target ticket type not found")
    if not new_type.is_active:
        raise ValueError("Target ticket type is not available")
    if new_type.requires_application:
        raise ValueError("Cannot upgrade to an application-based ticket")

    # Calculate difference
    current_paid = current_item.unit_price_eur * current_item.quantity
    new_price = new_type.price_eur * current_item.quantity

    if new_price <= current_paid:
        raise ValueError("Can only upgrade to a higher-priced ticket")

    price_diff = new_price - current_paid

    # TODO: Apply discount code to price_diff if provided

    return {
        "order_id": str(order.id),
        "current_ticket": current_type.name,
        "new_ticket": new_type.name,
        "current_price": current_paid,
        "new_price": new_price,
        "price_difference": price_diff,
        "quantity": current_item.quantity,
    }


async def apply_upgrade(
    db: AsyncSession, order_id: uuid.UUID, new_ticket_type_id: uuid.UUID
) -> Order:
    """Apply the upgrade: update the order item to the new ticket type."""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.items), selectinload(Order.attendee))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise ValueError("Order not found")

    current_item = order.items[0]

    # Get types
    result = await db.execute(select(TicketType).where(TicketType.id == current_item.ticket_type_id))
    old_type = result.scalar_one()
    result = await db.execute(select(TicketType).where(TicketType.id == new_ticket_type_id))
    new_type = result.scalar_one()

    # Update inventory
    old_type.quantity_sold -= current_item.quantity
    new_type.quantity_sold += current_item.quantity

    # Update order item
    current_item.ticket_type_id = new_type.id
    current_item.unit_price_eur = new_type.price_eur

    # Recalculate total
    order.total_eur = sum(item.unit_price_eur * item.quantity for item in order.items)

    await db.flush()

    # Reload
    result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    return result.scalar_one()
