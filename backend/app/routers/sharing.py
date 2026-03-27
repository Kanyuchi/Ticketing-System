import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from app.models.ticket_type import TicketType
from app.services.qr_service import generate_order_qr, generate_share_card

router = APIRouter(prefix="/sharing", tags=["sharing"])


@router.get("/qr/{order_id}")
async def get_order_qr(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Public: get QR code PNG for a confirmed order."""
    result = await db.execute(
        select(Order).where(Order.id == order_id).options(selectinload(Order.attendee))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Order is not confirmed")

    qr_bytes = generate_order_qr(order.id, order.order_number)
    return Response(content=qr_bytes, media_type="image/png")


@router.get("/card/{order_id}")
async def get_share_card(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Public: get 'I'm Attending' social card PNG for a confirmed order."""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    if order.status != OrderStatus.CONFIRMED:
        raise HTTPException(status_code=400, detail="Order is not confirmed")

    # Get ticket type name from first item
    ticket_type_name = "Attendee"
    if order.items:
        tt_result = await db.execute(
            select(TicketType).where(TicketType.id == order.items[0].ticket_type_id)
        )
        tt = tt_result.scalar_one_or_none()
        if tt:
            ticket_type_name = tt.name

    card_bytes = generate_share_card(order.attendee.name, ticket_type_name)
    return Response(content=card_bytes, media_type="image/png")


@router.get("/meta/{order_id}")
async def get_share_meta(order_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Public: get share metadata (URLs, text) for social sharing."""
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(selectinload(Order.attendee), selectinload(Order.items))
    )
    order = result.scalar_one_or_none()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    from app.core.config import settings

    card_url = f"{settings.frontend_url}/api/sharing/card/{order_id}"
    share_text = f"I'm attending Proof of Talk 2026! See you there."
    event_url = settings.frontend_url

    return {
        "share_text": share_text,
        "card_url": card_url,
        "event_url": event_url,
        "twitter_url": f"https://twitter.com/intent/tweet?text={share_text}&url={event_url}",
        "linkedin_url": f"https://www.linkedin.com/sharing/share-offsite/?url={event_url}",
    }
